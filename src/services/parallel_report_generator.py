from typing import Dict, Any, List
from src.services import llm_generator, ollama_llm_generator
from src.services.llm_validator import (
    validate_report,
    validate_retail_data_report,
    validate_email_performance_report,
    validate_social_media_data_report
)
from src.services.report_types import normalize_report_type
from src.models.validation_schema import ValidationResult
from src.config.settings import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor

import logging
import sys
from datetime import datetime

# Configure root logger for terminal output with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger("report-process")

def detect_report_type_from_data(context: dict) -> str:
    """
    Automatically detect the appropriate report type based on available data in context.
    This prevents content mismatch issues where social media reports are requested but only email data exists.
    """
    # Auto-detect based on data availability FIRST
    data = context.get('data', {})

    # Ensure data is a dictionary before calling .keys()
    if not isinstance(data, dict):
        logger.warning(f"Context data is not a dictionary: {type(data)}. Using default detection.")
        data = {}

    # Check for different data types with expanded keywords
    has_email_data = any(keyword in key.lower() for key in data.keys()
                        for keyword in ['email', 'send', 'open', 'click', 'unsubscribe', 'campaign'])
    has_retail_data = any(keyword in key.lower() for key in data.keys()
                         for keyword in ['sale', 'transaction', 'revenue', 'purchase', 'retail'])
    has_social_data = any(keyword in key.lower() for key in data.keys()
                         for keyword in ['follower', 'engagement', 'impression', 'like', 'share', 'post', 'platform'])

    # Prioritize based on data availability (social > email > retail)
    detected_type = 'all-categories'
    if has_social_data:
        detected_type = 'social-media-data'
    elif has_email_data:
        detected_type = 'email-performance-data'
    elif has_retail_data:
        detected_type = 'retail-data'



    # Check if requested type matches available data
    metadata = context.get('metadata', {})
    requested_type = metadata.get('reportType', 'all_categories')
    
    # Use shared normalizer to accept many input variants and produce canonical form
    requested_type = normalize_report_type(requested_type)




    # If requested type is 'all-categories', always use it (don't auto-detect)
    # all-categories reports contain data from multiple sources
    if requested_type == 'all-categories':
        return 'all-categories'

    # If no specific data detected, use requested type
    if detected_type == 'all-categories':
        return requested_type

    # If requested type matches detected data, use it
    if requested_type == detected_type:
        return requested_type

    # If there's a mismatch, prioritize detected data type over requested type
    # This prevents generating social media reports from email data
    return detected_type

def calculate_confidence_score(is_valid: bool, regeneration_attempts: int, previous_attempts: list, report_type: str) -> float:
    """
    Calculate confidence score for a report based on validation results and regeneration history.

    Scoring factors:
    - Base score: 1.0 for valid reports, 0.8 for invalid reports after max attempts
    - Regeneration penalty: -0.1 per regeneration attempt
    - Issue severity penalty: based on types of validation issues
    - Report type bonus: specialized reports get slight bonus for domain focus
    """
    base_score = 1.0 if is_valid else 0.8

    # Regeneration attempt penalty (max 3 attempts, so max penalty 0.3)
    regeneration_penalty = min(regeneration_attempts * 0.1, 0.3)

    # Issue severity penalty based on validation issues
    issue_penalty = 0.0
    if previous_attempts:
        total_issues = 0
        for attempt in previous_attempts:
            issues = attempt.get('issues', {})
            # Count issues in each category
            for category in ['structure', 'data_quality', 'content']:
                category_issues = issues.get(category)
                if category_issues and isinstance(category_issues, dict):
                    # Each issue reduces confidence by 0.02
                    issue_count = len([k for k, v in category_issues.items()
                                     if v and isinstance(v, list) and len(v) > 0])
                    total_issues += issue_count
        issue_penalty = min(total_issues * 0.02, 0.2)  # Max 0.2 penalty for issues

    # Report type bonus for specialized reports (they're more focused)
    # Accept both hyphen-separated and underscore variants by normalizing
    normalized_type_key = report_type.replace('-', '_') if isinstance(report_type, str) else report_type
    type_bonus = 0.05 if normalized_type_key in ['retail_data', 'email_performance', 'social_media_data'] else 0.0

    # Calculate final score
    confidence_score = max(0.0, min(1.0, base_score - regeneration_penalty - issue_penalty + type_bonus))

    return round(confidence_score, 3)

class ParallelReportGenerator:
    def __init__(self):
        self.max_retries = settings.MAX_RETRIES
        self.parallel_generation = settings.PARALLEL_GENERATION
        self.require_dual_validation = settings.REQUIRE_DUAL_VALIDATION
        self.min_consistency_score = settings.MIN_CONSISTENCY_SCORE
        
    async def regenerate_invalid_report(self, structure: dict, context: dict, source: str, previous_validation: dict) -> dict:
        """Regenerate a report that failed validation"""
        logger.info(f"Regenerating {source} report after validation failure")
        
        # Include validation feedback in context
        feedback = {
            "previous_validation": previous_validation,
            "attempt": 1,  # Track regeneration attempts
            "issues_to_fix": previous_validation["details"]["validation_results"] if previous_validation["details"] else None
        }
        
        try:
            if source == "Gemini":
                report = llm_generator.generate_report(structure, context, feedback)
            else:
                report = ollama_llm_generator.generate_report(structure, context, feedback)
                
            # Validate regenerated report
            validation = validate_report(structure, report)
            
            # Calculate confidence score for regenerated report
            confidence_score = calculate_confidence_score(validation.is_valid, 1, [], "all_categories")
            return {
                "source": source,
                "report": report,
                "validation": {
                    "is_valid": validation.is_valid,
                    "message": validation.message,
                    "details": validation.detailed_results.dict() if validation.detailed_results else None
                },
                "regeneration_attempt": 1,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error regenerating {source} report: {str(e)}")
            return None

    async def generate_reports(self, structure: dict, context: dict) -> List[dict]:
        """
        Generate reports in parallel using multiple LLMs and validate/regenerate each as soon as it is ready.
        If validation fails, provide targeted feedback and regenerate only problematic fields, up to 3 attempts per report.
        """
        from src.services.report_regenerator import ReportRegenerator
        try:
            if self.parallel_generation:
                    with ThreadPoolExecutor() as executor:
                        loop = asyncio.get_event_loop()
                        # Prepare futures and log start immediately
                        futures = []
                        future_to_source = {}

                        # Determine which generator and validator functions to use based on report type
                        # Auto-detect report type from available data to prevent content mismatch
                        report_type = detect_report_type_from_data(context)
                        logger.info(f"Detected report type: {report_type}")

                        if report_type == "retail-data":
                            gemini_func = llm_generator.generate_retail_data_report
                            ollama_func = ollama_llm_generator.generate_retail_data_report
                            validate_func = validate_retail_data_report
                        elif report_type == "email-performance-data":
                            gemini_func = llm_generator.generate_email_performance_report
                            ollama_func = ollama_llm_generator.generate_email_performance_report
                            validate_func = validate_email_performance_report
                        elif report_type == "social-media-data":
                            gemini_func = llm_generator.generate_social_media_data_report
                            ollama_func = ollama_llm_generator.generate_social_media_data_report
                            validate_func = validate_social_media_data_report
                        else:  # all-categories or unknown
                            gemini_func = llm_generator.generate_report
                            ollama_func = ollama_llm_generator.generate_report
                            validate_func = validate_report

                        for source_name, generator_func in [
                            ("Gemini", gemini_func),
                            ("Ollama", ollama_func)
                        ]:
                            logger.info(f"[{source_name}] Report generation started.")
                            fut = loop.run_in_executor(
                                executor,
                                generator_func,
                                structure,
                                context,
                                None
                            )
                            futures.append(fut)
                            future_to_source[fut] = source_name

                    logger.info("Starting parallel report generation for: %s", ', '.join(future_to_source.values()))
                    results = []
                    async for completed_future in asyncio.as_completed(futures):
                        source_name = future_to_source[completed_future]
                        try:
                            report = await completed_future
                            logger.info(f"[{source_name}] Report generation completed. Starting validation.")
                            validation = validate_func(structure, report)
                            logger.info(f"[{source_name}] Validation completed. Result: {'VALID' if validation.is_valid else 'INVALID'}.")

                            # Print detailed validator response to terminal
                            print(f"\n=== VALIDATOR RESPONSE FOR {source_name} ===")
                            print(f"Valid: {validation.is_valid}")
                            print(f"Message: {validation.message}")
                            if validation.detailed_results:
                                print(f"Detailed Results: {validation.detailed_results.dict()}")
                            print("=" * 50)
                            attempt = 0
                            max_attempts = 1  # Ensure up to 3 regeneration attempts
                            previous_attempts = []
                            while not validation.is_valid and attempt < max_attempts:
                                attempt += 1
                                logger.info(f"[{source_name}] Validation failed. Attempting targeted regeneration (Attempt {attempt}/{max_attempts})...")
                                details = validation.detailed_results
                                if details and details.regeneration_required and details.regenerate_fields:
                                    regenerator = ReportRegenerator(structure, context, report)
                                    regen_prompt = regenerator.create_regeneration_prompt(details, previous_attempts)
                                    logger.info(f"[{source_name}] Regenerating fields: {details.regenerate_fields}")

                                    # Use appropriate generator function for regeneration
                                    if report_type == "retail-data":
                                        regen_gemini_func = llm_generator.generate_retail_data_report
                                        regen_ollama_func = ollama_llm_generator.generate_retail_data_report
                                    elif report_type == "email-performance-data":
                                        regen_gemini_func = llm_generator.generate_email_performance_report
                                        regen_ollama_func = ollama_llm_generator.generate_email_performance_report
                                    elif report_type == "social-media-data":
                                        regen_gemini_func = llm_generator.generate_social_media_data_report
                                        regen_ollama_func = ollama_llm_generator.generate_social_media_data_report
                                    else:
                                        regen_gemini_func = llm_generator.generate_report
                                        regen_ollama_func = ollama_llm_generator.generate_report

                                    if source_name == "Gemini":
                                        regenerated_report = regen_gemini_func(structure, context, {"regeneration_prompt": regen_prompt})
                                    else:
                                        regenerated_report = regen_ollama_func(structure, context, {"regeneration_prompt": regen_prompt})

                                    logger.info(f"[{source_name}] Regeneration completed. Re-validating...")
                                    validation = validate_func(structure, regenerated_report)
                                    logger.info(f"[{source_name}] Re-validation result: {'VALID' if validation.is_valid else 'INVALID'}.")
                                    previous_attempts.append({
                                        "attempt": attempt,
                                        "fields_regenerated": details.regenerate_fields,
                                        "issues": {
                                            "structure": details.validation_results.structure.dict() if details.validation_results else None,
                                            "data_quality": details.validation_results.data_quality.dict() if details.validation_results else None,
                                            "content": details.validation_results.content.dict() if details.validation_results else None
                                        }
                                    })
                                    report = regenerated_report
                                else:
                                    logger.info(f"[{source_name}] No fields to regenerate or missing details. Stopping regeneration attempts.")
                                    break

                            # Calculate confidence score based on validation results and attempts
                            confidence_score = calculate_confidence_score(validation.is_valid, attempt, previous_attempts, report_type)
                            result = {
                                "source": source_name,
                                "report": report,
                                "validation": {
                                    "is_valid": validation.is_valid,
                                    "message": validation.message,
                                    "details": validation.detailed_results.dict() if validation.detailed_results else None
                                },
                                "regeneration_attempt": attempt,
                                "confidence_score": confidence_score
                            }
                            logger.info(f"[{source_name}] Final result: {'VALID' if validation.is_valid else 'INVALID'} after {attempt} regeneration attempts.")
                            results.append(result)
                        except Exception as e:
                            logger.error(f"[{source_name}] Error generating or validating report: {str(e)}")
                    if not results:
                        logger.error("All report generations failed")
                        raise ValueError("All report generations failed")
                    logger.info("Parallel report generation and validation complete.")
                    return results
            else:
                # Sequential generation (unchanged)
                results = []
                for source_name, generator_func in [("Gemini", llm_generator.generate_report), ("Ollama", ollama_llm_generator.generate_report)]:
                    report = generator_func(structure, context)
                    if report:
                        validation = validate_report(structure, report)
                        attempt = 0
                        max_attempts = self.max_retries
                        previous_attempts = []
                        while not validation.is_valid and attempt < max_attempts:
                            attempt += 1
                            details = validation.detailed_results
                            if details and details.regeneration_required and details.regenerate_fields:
                                regenerator = ReportRegenerator(structure, context, report)
                                regen_prompt = regenerator.create_regeneration_prompt(details, previous_attempts)
                                if source_name == "Gemini":
                                    regenerated_report = llm_generator.generate_report(structure, context, {"regeneration_prompt": regen_prompt})
                                else:
                                    regenerated_report = ollama_llm_generator.generate_report(structure, context, {"regeneration_prompt": regen_prompt})
                                validation = validate_report(structure, regenerated_report)
                                previous_attempts.append({
                                    "attempt": attempt,
                                    "fields_regenerated": details.regenerate_fields,
                                    "issues": {
                                        "structure": details.validation_results.structure.dict(),
                                        "data_quality": details.validation_results.data_quality.dict(),
                                        "content": details.validation_results.content.dict()
                                    }
                                })
                                report = regenerated_report
                            else:
                                break
                        # Calculate confidence score for sequential generation too
                        confidence_score = calculate_confidence_score(validation.is_valid, attempt, previous_attempts, "all-categories")
                        result = {
                            "source": source_name,
                            "report": report,
                            "validation": {
                                "is_valid": validation.is_valid,
                                "message": validation.message,
                                "details": validation.detailed_results.dict() if validation.detailed_results else None
                            },
                            "regeneration_attempt": attempt,
                            "confidence_score": confidence_score
                        }
                        results.append(result)
                return results
        except Exception as e:
            logger.error(f"Error in parallel report generation: {str(e)}")
            raise
