from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class LoanType(str, Enum):
    VARIABLE = "variable"
    FIXED = "fixed"
    SPLIT = "split"

class RepaymentType(str, Enum):
    PRINCIPAL_AND_INTEREST = "principal_and_interest"
    INTEREST_ONLY = "interest_only"

class LoanProduct(BaseModel):
    id: str = Field(..., description="Unique product identifier")
    bank_name: str = Field(..., description="Name of the lending bank")
    product_name: str = Field(..., description="Name of the loan product")
    loan_type: LoanType = Field(..., description="Type of interest rate")
    interest_rate: float = Field(..., description="Current interest rate (%)")
    comparison_rate: float = Field(..., description="Comparison rate (%)")
    
    # Fees
    application_fee: Optional[float] = Field(None, description="One-time application fee")
    ongoing_fee: Optional[float] = Field(None, description="Monthly/annual ongoing fee")
    exit_fee: Optional[float] = Field(None, description="Early exit fee")
    
    # Eligibility criteria
    min_loan_amount: int = Field(50000, description="Minimum loan amount")
    max_loan_amount: int = Field(2000000, description="Maximum loan amount")
    max_lvr: float = Field(95.0, description="Maximum loan-to-value ratio (%)")
    min_income: Optional[int] = Field(None, description="Minimum annual income required")
    
    # Features
    offset_account: bool = Field(False, description="Offers offset account")
    redraw_facility: bool = Field(False, description="Has redraw facility")
    extra_repayments: bool = Field(True, description="Allows extra repayments")
    repayment_types: List[RepaymentType] = Field(default_factory=list)
    
    # Additional criteria
    first_home_buyer_only: bool = Field(False, description="Restricted to first home buyers")
    investment_property_allowed: bool = Field(True, description="Allows investment properties")
    self_employed_accepted: bool = Field(True, description="Accepts self-employed applicants")
    
    # Metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    source_document: Optional[str] = Field(None, description="Source document reference")

class LoanRecommendation(BaseModel):
    loan_product: LoanProduct
    match_score: float = Field(..., description="Match score (0-100)", ge=0, le=100)
    confidence_score: float = Field(..., description="AI confidence (0-100)", ge=0, le=100)
    reasoning: str = Field(..., description="Why this loan is recommended")
    estimated_monthly_payment: float = Field(..., description="Estimated monthly payment")
    total_fees_estimate: float = Field(..., description="Estimated total fees")
    eligibility_check: Dict[str, Any] = Field(default_factory=dict, description="Detailed eligibility analysis")
    warnings: List[str] = Field(default_factory=list, description="Potential issues or warnings")

class RecommendationResponse(BaseModel):
    client_profile_summary: Dict[str, Any]
    recommendations: List[LoanRecommendation]
    processing_time_seconds: float
    total_products_analyzed: int
    ai_confidence: str  # "high", "medium", "low"
    broker_review_suggested: bool