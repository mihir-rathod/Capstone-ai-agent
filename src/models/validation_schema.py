from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ValidationIssue(BaseModel):
    field: str
    issue: str
    fix: str

class ValidationSection(BaseModel):
    passed: bool
    issues: List[ValidationIssue] = []

class ValidationResults(BaseModel):
    structure: ValidationSection
    data_quality: ValidationSection
    content: ValidationSection

class MergeRecommendation(BaseModel):
    field: str
    recommendation: str
    source: str = Field(..., description="Source of the recommendation: 'report_0', 'report_1', or 'both'")

class ReportComparison(BaseModel):
    best_report_index: int
    reason: str
    consistency_score: float
    unique_insights: Dict[str, List[str]]

class FinalDecision(BaseModel):
    use_best_report: bool
    fields_to_merge: List[str] = []

class DetailedValidationResult(BaseModel):
    is_valid: bool
    validation_results: ValidationResults
    summary: str
    regeneration_required: bool = False
    regenerate_fields: List[str] = []
    report_comparison: Optional[ReportComparison] = None
    merge_recommendations: Optional[List[MergeRecommendation]] = None
    final_decision: Optional[FinalDecision] = None

class ValidationResult(BaseModel):
    """
    Simplified validation result for API responses.
    Contains the essential validation information while preserving
    backward compatibility.
    """
    is_valid: bool
    message: str
    detailed_results: Optional[DetailedValidationResult] = None
