from typing import Dict, Any, List
from src.services import llm_generator, ollama_llm_generator
from src.services.llm_validator import validate_report
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
            
            return {
                "source": source,
                "report": report,
                "validation": {
                    "is_valid": validation.is_valid,
                    "message": validation.message,
                    "details": validation.detailed_results.dict() if validation.detailed_results else None
                },
                "regeneration_attempt": 1
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
                    for source_name, generator_func in [
                        ("Gemini", llm_generator.generate_report),
                        ("Ollama", ollama_llm_generator.generate_report)
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
                            validation = validate_report(structure, report)
                            logger.info(f"[{source_name}] Validation completed. Result: {'VALID' if validation.is_valid else 'INVALID'}.")
                            attempt = 0
                            max_attempts = self.max_retries
                            previous_attempts = []
                            while not validation.is_valid and attempt < max_attempts:
                                attempt += 1
                                logger.info(f"[{source_name}] Validation failed. Attempting targeted regeneration (Attempt {attempt}/{max_attempts})...")
                                details = validation.detailed_results
                                if details and details.regeneration_required and details.regenerate_fields:
                                    regenerator = ReportRegenerator(structure, context, report)
                                    regen_prompt = regenerator.create_regeneration_prompt(details, previous_attempts)
                                    logger.info(f"[{source_name}] Regenerating fields: {details.regenerate_fields}")
                                    if source_name == "Gemini":
                                        regenerated_report = llm_generator.generate_report(structure, context, {"regeneration_prompt": regen_prompt})
                                    else:
                                        regenerated_report = ollama_llm_generator.generate_report(structure, context, {"regeneration_prompt": regen_prompt})
                                    logger.info(f"[{source_name}] Regeneration completed. Re-validating...")
                                    validation = validate_report(structure, regenerated_report)
                                    logger.info(f"[{source_name}] Re-validation result: {'VALID' if validation.is_valid else 'INVALID'}.")
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
                                    logger.info(f"[{source_name}] No fields to regenerate or missing details. Stopping regeneration attempts.")
                                    break
                            result = {
                                "source": source_name,
                                "report": report,
                                "validation": {
                                    "is_valid": validation.is_valid,
                                    "message": validation.message,
                                    "details": validation.detailed_results.dict() if validation.detailed_results else None
                                },
                                "regeneration_attempt": attempt
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
                        result = {
                            "source": source_name,
                            "report": report,
                            "validation": {
                                "is_valid": validation.is_valid,
                                "message": validation.message,
                                "details": validation.detailed_results.dict() if validation.detailed_results else None
                            },
                            "regeneration_attempt": attempt
                        }
                        results.append(result)
                return results
        except Exception as e:
            logger.error(f"Error in parallel report generation: {str(e)}")
            raise