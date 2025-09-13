#!/usr/bin/env python3
"""
Comprehensive Eligibility Checker - Automated yes/no based on all criteria
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sys
import os

# Import our other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from income_calculator import IncomeCalculator, IncomeSource, IncomeType
from property_classifier import PropertyClassifier, PropertyDetails, PropertyType as PropType, PropertyCategory
from serviceability_calculator import ServiceabilityCalculator
from risk_scoring import RiskScoringSystem, RiskFactors, RiskGrade
from matching_engine import LenderMatchingEngine, ClientProfile, EmploymentType

class EligibilityDecision(Enum):
    APPROVED = "approved"
    CONDITIONAL_APPROVAL = "conditional"
    DECLINED = "declined"
    REFER_TO_SPECIALIST = "refer_specialist"

@dataclass
class EligibilityResult:
    decision: EligibilityDecision
    approved_lenders: List[str]
    declined_lenders: List[str]
    conditional_lenders: List[str]
    overall_confidence: float
    key_decision_factors: List[str]
    required_conditions: List[str]
    recommendations: List[str]
    risk_grade: RiskGrade
    max_loan_amount: float
    estimated_interest_rate: float

@dataclass
class ComprehensiveLoanApplication:
    # Personal Details
    annual_income: float
    employment_type: str
    employment_months: int
    credit_score: int
    existing_monthly_debts: float
    monthly_expenses: float
    dependents: int
    is_couple: bool
    first_home_buyer: bool
    
    # Loan Details
    requested_loan_amount: float
    property_value: float
    deposit_amount: float
    loan_term_years: int
    
    # Property Details
    property_type: str
    living_area_sqm: int
    postcode: str
    land_size_hectares: float = 0.0
    floors_in_building: Optional[int] = None
    units_in_building: Optional[int] = None
    heritage_listed: bool = False
    flood_prone: bool = False
    bushfire_zone: bool = False
    
    # Additional Risk Factors
    previous_defaults: int = 0
    bankruptcy_history: bool = False
    deposit_source: str = "genuine_savings"
    borrowing_history: str = "good"

class ComprehensiveEligibilityChecker:
    
    def __init__(self):
        self.income_calculator = IncomeCalculator()
        self.property_classifier = PropertyClassifier()
        self.serviceability_calculator = ServiceabilityCalculator()
        self.risk_scorer = RiskScoringSystem()
        self.matching_engine = LenderMatchingEngine()
        
        # Decision thresholds
        self.approval_thresholds = {
            "min_risk_score": 50,  # Above this = decline
            "min_serviceability_buffer": 0.1,  # 10% NDI buffer minimum
            "max_dti_ratio": 8.0,  # Maximum debt-to-income
            "min_credit_score": 500,  # Below this = decline
            "max_lvr_any_lender": 95  # No lender accepts above this
        }
    
    def check_comprehensive_eligibility(self, application: ComprehensiveLoanApplication) -> EligibilityResult:
        """
        Main eligibility checking function that combines all components
        """
        
        # Step 1: Basic eligibility checks
        basic_eligibility = self._check_basic_eligibility(application)
        if not basic_eligibility["eligible"]:
            return self._create_decline_result(basic_eligibility["reasons"])
        
        # Step 2: Property classification
        property_details = self._create_property_details(application)
        property_classification = self.property_classifier.classify_property(property_details)
        
        if property_classification.category == PropertyCategory.UNACCEPTABLE:
            return self._create_decline_result(
                ["Property type/characteristics unacceptable to lenders"] + property_classification.reasons
            )
        
        # Step 3: Income assessment
        income_assessment = self._assess_income(application)
        if not income_assessment["sufficient"]:
            return self._create_decline_result(income_assessment["reasons"])
        
        # Step 4: Serviceability assessment
        serviceability = self.serviceability_calculator.calculate_serviceability(
            gross_annual_income=income_assessment["total_usable_income"],
            monthly_expenses=application.monthly_expenses,
            existing_monthly_debts=application.existing_monthly_debts,
            proposed_loan_amount=application.requested_loan_amount,
            interest_rate=6.0,  # Average rate for assessment
            loan_term_years=application.loan_term_years,
            dependents=application.dependents,
            is_couple=application.is_couple
        )
        
        if not serviceability.can_service:
            return self._create_decline_result(
                ["Cannot service requested loan amount"] + serviceability.warnings
            )
        
        # Step 5: Risk assessment
        risk_factors = self._create_risk_factors(application, serviceability.dti_ratio)
        risk_assessment = self.risk_scorer.assess_borrower_risk(risk_factors)
        
        # Step 6: Lender matching
        client_profile = self._create_client_profile(application)
        lender_matches = self.matching_engine.match_all_lenders(client_profile)
        
        # Step 7: Calculate maximum borrowing capacity
        max_capacity = self.serviceability_calculator.calculate_maximum_borrowing_capacity(
            income_assessment["total_usable_income"],
            application.monthly_expenses,
            application.existing_monthly_debts,
            6.0,  # Average interest rate
            application.loan_term_years
        )
        
        # Step 8: Make final decision
        return self._make_final_decision(
            application, property_classification, serviceability, 
            risk_assessment, lender_matches, max_capacity
        )
    
    def _check_basic_eligibility(self, app: ComprehensiveLoanApplication) -> Dict:
        """Basic eligibility checks that immediately disqualify"""
        
        reasons = []
        
        # Age check (assuming minimum 18)
        # Credit score minimum
        if app.credit_score < self.approval_thresholds["min_credit_score"]:
            reasons.append(f"Credit score {app.credit_score} below minimum {self.approval_thresholds['min_credit_score']}")
        
        # Income minimum
        if app.annual_income < 30000:
            reasons.append(f"Annual income ${app.annual_income:,.0f} below minimum $30,000")
        
        # LVR maximum
        lvr = (app.requested_loan_amount / app.property_value) * 100
        if lvr > self.approval_thresholds["max_lvr_any_lender"]:
            reasons.append(f"LVR {lvr:.1f}% exceeds maximum acceptable {self.approval_thresholds['max_lvr_any_lender']}%")
        
        # Bankruptcy check
        if app.bankruptcy_history:
            reasons.append("Undischarged bankruptcy - no lenders will accept")
        
        # Loan amount sanity check
        if app.requested_loan_amount <= 0 or app.property_value <= 0:
            reasons.append("Invalid loan amount or property value")
        
        return {
            "eligible": len(reasons) == 0,
            "reasons": reasons
        }
    
    def _create_property_details(self, app: ComprehensiveLoanApplication) -> PropertyDetails:
        """Convert application to PropertyDetails for classification"""
        
        # Map string property type to enum
        prop_type_mapping = {
            "house": PropType.HOUSE,
            "unit": PropType.UNIT,
            "apartment": PropType.APARTMENT,
            "townhouse": PropType.TOWNHOUSE,
            "villa": PropType.VILLA,
            "studio_apartment": PropType.STUDIO_APARTMENT,
            "rural_residential": PropType.RURAL_RESIDENTIAL,
            "vacant_land": PropType.VACANT_LAND
        }
        
        prop_type = prop_type_mapping.get(app.property_type, PropType.HOUSE)
        
        return PropertyDetails(
            property_type=prop_type,
            living_area_sqm=app.living_area_sqm,
            land_size_hectares=app.land_size_hectares,
            property_value=int(app.property_value),
            postcode=app.postcode,
            floors_in_building=app.floors_in_building,
            units_in_building=app.units_in_building,
            heritage_listed=app.heritage_listed,
            flood_prone=app.flood_prone,
            bushfire_zone=app.bushfire_zone
        )
    
    def _assess_income(self, app: ComprehensiveLoanApplication) -> Dict:
        """Assess income sufficiency"""
        
        # For simplicity, create a single primary income source
        # In a real system, this would be multiple sources
        employment_type_mapping = {
            "permanent": IncomeType.PAYG_PERMANENT,
            "casual": IncomeType.PAYG_CASUAL,
            "self_employed": IncomeType.SELF_EMPLOYED,
            "contract": IncomeType.PAYG_CONTRACT
        }
        
        income_type = employment_type_mapping.get(app.employment_type, IncomeType.PAYG_PERMANENT)
        
        income_source = IncomeSource(
            income_type=income_type,
            gross_amount=app.annual_income,
            frequency="annually",
            employment_months=app.employment_months
        )
        
        result = self.income_calculator.calculate_usable_income([income_source])
        
        # Check if income is sufficient for basic living plus loan
        estimated_monthly_payment = self.serviceability_calculator._calculate_monthly_payment(
            app.requested_loan_amount, 0.06, app.loan_term_years
        )
        
        monthly_income = result.total_usable_income / 12
        required_income = app.monthly_expenses + app.existing_monthly_debts + estimated_monthly_payment
        
        sufficient = monthly_income > required_income * 1.1  # Need 10% buffer
        
        reasons = []
        if not sufficient:
            reasons.append(f"Income insufficient: ${monthly_income:,.0f}/month available vs ${required_income:,.0f}/month required")
        
        reasons.extend(result.warnings)
        
        return {
            "sufficient": sufficient,
            "total_usable_income": result.total_usable_income,
            "reasons": reasons,
            "employment_stability": result.employment_stability_score
        }
    
    def _create_risk_factors(self, app: ComprehensiveLoanApplication, dti_ratio: float) -> RiskFactors:
        """Create risk factors for risk assessment"""
        
        lvr = (app.requested_loan_amount / app.property_value) * 100
        
        return RiskFactors(
            credit_score=app.credit_score,
            employment_stability=app.employment_type,
            employment_months=app.employment_months,
            income_consistency=0.85,  # Default assumption
            debt_to_income=dti_ratio,
            loan_to_value=lvr,
            deposit_source=app.deposit_source,
            previous_defaults=app.previous_defaults,
            bankruptcy_history=app.bankruptcy_history,
            property_type=app.property_type,
            location_risk="medium",  # Default assumption
            borrowing_history=app.borrowing_history
        )
    
    def _create_client_profile(self, app: ComprehensiveLoanApplication) -> ClientProfile:
        """Convert application to ClientProfile for lender matching"""
        
        # Map employment types
        emp_type_mapping = {
            "permanent": EmploymentType.PAYG_PERMANENT,
            "casual": EmploymentType.PAYG_CASUAL,
            "self_employed": EmploymentType.SELF_EMPLOYED,
            "contract": EmploymentType.CONTRACT
        }
        
        prop_type_mapping = {
            "house": PropType.HOUSE,
            "unit": PropType.UNIT,
            "townhouse": PropType.TOWNHOUSE,
            "rural_residential": PropType.RURAL_RESIDENTIAL,
            "studio_apartment": PropType.STUDIO_APARTMENT
        }
        
        return ClientProfile(
            annual_income=int(app.annual_income),
            loan_amount=int(app.requested_loan_amount),
            property_value=int(app.property_value),
            property_type=prop_type_mapping.get(app.property_type, PropType.HOUSE),
            employment_type=emp_type_mapping.get(app.employment_type, EmploymentType.PAYG_PERMANENT),
            employment_months=app.employment_months,
            deposit=int(app.deposit_amount),
            existing_debts=int(app.existing_monthly_debts * 12),  # Convert to annual
            credit_score=app.credit_score,
            first_home_buyer=app.first_home_buyer
        )
    
    def _make_final_decision(self, application, property_class, serviceability, 
                           risk_assessment, lender_matches, max_capacity) -> EligibilityResult:
        """Make the final eligibility decision"""
        
        approved_lenders = []
        declined_lenders = []
        conditional_lenders = []
        decision_factors = []
        conditions = []
        recommendations = []
        
        # Analyze lender matches
        for match in lender_matches:
            if match.eligible and match.match_score >= 70:
                approved_lenders.append(match.lender_name)
            elif match.eligible and match.match_score >= 50:
                conditional_lenders.append(match.lender_name)
            else:
                declined_lenders.append(match.lender_name)
        
        # Determine overall decision
        if len(approved_lenders) > 0:
            decision = EligibilityDecision.APPROVED
            decision_factors.append(f"Approved by {len(approved_lenders)} lender(s)")
        elif len(conditional_lenders) > 0:
            decision = EligibilityDecision.CONDITIONAL_APPROVAL
            decision_factors.append(f"Conditional approval from {len(conditional_lenders)} lender(s)")
        elif risk_assessment.risk_grade in [RiskGrade.C_GRADE]:
            decision = EligibilityDecision.REFER_TO_SPECIALIST
            decision_factors.append("Refer to specialist lenders for manual assessment")
        else:
            decision = EligibilityDecision.DECLINED
            decision_factors.append("No suitable lenders found")
        
        # Add key decision factors
        decision_factors.append(f"Risk Grade: {risk_assessment.risk_grade.value}")
        decision_factors.append(f"LVR: {(application.requested_loan_amount/application.property_value)*100:.1f}%")
        decision_factors.append(f"DTI: {serviceability.dti_ratio:.1f}")
        decision_factors.append(f"Property: {property_class.category.value}")
        
        # Generate conditions for conditional approvals
        if decision == EligibilityDecision.CONDITIONAL_APPROVAL:
            conditions.extend(serviceability.recommendations)
            conditions.extend(risk_assessment.recommendations[:2])
            
            if property_class.warnings:
                conditions.extend([f"Property: {w}" for w in property_class.warnings[:1]])
        
        # Generate recommendations
        if decision == EligibilityDecision.APPROVED:
            recommendations.append("Strong application - negotiate for better interest rates")
            if max_capacity > application.requested_loan_amount * 1.2:
                recommendations.append(f"Could potentially borrow up to ${max_capacity:,.0f}")
        
        elif decision == EligibilityDecision.CONDITIONAL_APPROVAL:
            recommendations.append("Address conditions to improve approval chances")
            recommendations.extend(risk_assessment.recommendations[:2])
        
        elif decision == EligibilityDecision.REFER_TO_SPECIALIST:
            recommendations.append("Consider specialist or non-bank lenders")
            recommendations.append("May require higher interest rates or fees")
            recommendations.extend(risk_assessment.recommendations[:1])
        
        else:  # DECLINED
            recommendations.append("Improve risk profile before reapplying")
            recommendations.extend(risk_assessment.recommendations[:3])
        
        # Calculate overall confidence
        confidence_factors = [
            serviceability.ndi_ratio if serviceability.ndi_ratio > 0 else 0,
            risk_assessment.grade_confidence,
            1.0 if property_class.category != PropertyCategory.UNACCEPTABLE else 0.0,
            len(approved_lenders + conditional_lenders) / 3.0  # Normalize to number of lenders
        ]
        
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Estimate interest rate
        if approved_lenders and lender_matches:
            estimated_rate = min([m.interest_rate for m in lender_matches if m.eligible])
        elif risk_assessment.risk_grade == RiskGrade.C_GRADE:
            estimated_rate = 7.5  # Higher rate for specialist lenders
        else:
            estimated_rate = 6.5  # Default rate
        
        return EligibilityResult(
            decision=decision,
            approved_lenders=approved_lenders,
            declined_lenders=declined_lenders,
            conditional_lenders=conditional_lenders,
            overall_confidence=overall_confidence,
            key_decision_factors=decision_factors,
            required_conditions=conditions,
            recommendations=recommendations,
            risk_grade=risk_assessment.risk_grade,
            max_loan_amount=max_capacity,
            estimated_interest_rate=estimated_rate
        )
    
    def _create_decline_result(self, reasons: List[str]) -> EligibilityResult:
        """Create a decline result with reasons"""
        return EligibilityResult(
            decision=EligibilityDecision.DECLINED,
            approved_lenders=[],
            declined_lenders=["All Lenders"],
            conditional_lenders=[],
            overall_confidence=0.0,
            key_decision_factors=reasons,
            required_conditions=[],
            recommendations=["Address fundamental eligibility issues before reapplying"],
            risk_grade=RiskGrade.DECLINE,
            max_loan_amount=0.0,
            estimated_interest_rate=0.0
        )

# Example usage and testing
def test_eligibility_checker():
    """Test the comprehensive eligibility checker"""
    
    checker = ComprehensiveEligibilityChecker()
    
    # Test case 1: Strong application
    strong_application = ComprehensiveLoanApplication(
        annual_income=95000,
        employment_type="permanent",
        employment_months=36,
        credit_score=750,
        existing_monthly_debts=500,
        monthly_expenses=3200,
        dependents=1,
        is_couple=True,
        first_home_buyer=True,
        requested_loan_amount=520000,
        property_value=650000,
        deposit_amount=130000,
        loan_term_years=30,
        property_type="house",
        living_area_sqm=120,
        postcode="3141",
        land_size_hectares=0.5,
        deposit_source="genuine_savings"
    )
    
    # Test case 2: Marginal application
    marginal_application = ComprehensiveLoanApplication(
        annual_income=65000,
        employment_type="casual",
        employment_months=8,
        credit_score=620,
        existing_monthly_debts=800,
        monthly_expenses=3500,
        dependents=0,
        is_couple=False,
        first_home_buyer=False,
        requested_loan_amount=450000,
        property_value=500000,
        deposit_amount=50000,
        loan_term_years=30,
        property_type="unit",
        living_area_sqm=55,
        postcode="3000",
        deposit_source="gift"
    )
    
    test_cases = [
        ("Strong Application", strong_application),
        ("Marginal Application", marginal_application)
    ]
    
    for name, application in test_cases:
        print(f"=== {name} ===")
        print(f"Income: ${application.annual_income:,}, Loan: ${application.requested_loan_amount:,}")
        print(f"LVR: {(application.requested_loan_amount/application.property_value)*100:.1f}%, Credit Score: {application.credit_score}")
        print()
        
        result = checker.check_comprehensive_eligibility(application)
        
        print(f"DECISION: {result.decision.value.upper()}")
        print(f"Risk Grade: {result.risk_grade.value}")
        print(f"Confidence: {result.overall_confidence:.1%}")
        print()
        
        if result.approved_lenders:
            print(f"Approved Lenders: {', '.join(result.approved_lenders)}")
        
        if result.conditional_lenders:
            print(f"Conditional Lenders: {', '.join(result.conditional_lenders)}")
        
        if result.declined_lenders and result.declined_lenders != ["All Lenders"]:
            print(f"Declined Lenders: {', '.join(result.declined_lenders)}")
        
        print(f"Estimated Rate: {result.estimated_interest_rate:.2f}%")
        print(f"Max Borrowing Capacity: ${result.max_loan_amount:,.0f}")
        print()
        
        print("Key Decision Factors:")
        for factor in result.key_decision_factors:
            print(f"  • {factor}")
        print()
        
        if result.required_conditions:
            print("Required Conditions:")
            for condition in result.required_conditions:
                print(f"  • {condition}")
            print()
        
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  • {rec}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_eligibility_checker()