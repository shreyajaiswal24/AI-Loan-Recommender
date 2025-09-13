#!/usr/bin/env python3
"""
Lender Matching Engine - Automatically matches clients to suitable lenders
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class PropertyType(Enum):
    HOUSE = "house"
    UNIT = "unit"
    TOWNHOUSE = "townhouse"
    RURAL_RESIDENTIAL = "rural_residential"
    STUDIO_APARTMENT = "studio_apartment"

class EmploymentType(Enum):
    PAYG_PERMANENT = "payg_permanent"
    PAYG_CASUAL = "payg_casual"
    SELF_EMPLOYED = "self_employed"
    CONTRACT = "contract"

@dataclass
class ClientProfile:
    annual_income: int
    loan_amount: int
    property_value: int
    property_type: PropertyType
    employment_type: EmploymentType
    employment_months: int
    deposit: int
    existing_debts: int
    credit_score: int = 700
    first_home_buyer: bool = False

@dataclass 
class LenderMatch:
    lender_name: str
    eligible: bool
    match_score: float  # 0-100
    reasons: List[str]
    warnings: List[str]
    interest_rate: float = 0.0

class LenderMatchingEngine:
    def __init__(self, criteria_file: str = "data/lender_criteria.json"):
        with open(criteria_file, 'r') as f:
            self.criteria = json.load(f)
    
    def calculate_lvr(self, loan_amount: int, property_value: int) -> float:
        """Calculate Loan-to-Value Ratio"""
        return (loan_amount / property_value) * 100
    
    def calculate_dti(self, total_debt: int, annual_income: int) -> float:
        """Calculate Debt-to-Income Ratio"""
        return total_debt / annual_income
    
    def match_great_southern_bank(self, client: ClientProfile) -> LenderMatch:
        """Match client against Great Southern Bank criteria"""
        criteria = self.criteria["lenders"]["great_southern_bank"]
        
        eligible = True
        reasons = []
        warnings = []
        score = 100
        
        # Calculate key ratios
        lvr = self.calculate_lvr(client.loan_amount, client.property_value)
        total_debt = client.loan_amount + client.existing_debts
        dti = self.calculate_dti(total_debt, client.annual_income)
        
        # Check LVR limits
        loan_purpose = "owner_occupied" if client.first_home_buyer else "investment"
        
        if lvr <= criteria["lvr_limits"][loan_purpose]["without_lmi"]:
            reasons.append(f"LVR {lvr:.1f}% within standard limits")
        elif lvr <= criteria["lvr_limits"][loan_purpose]["with_lmi"]:
            reasons.append(f"LVR {lvr:.1f}% acceptable with LMI")
        else:
            eligible = False
            score -= 50
            warnings.append(f"LVR {lvr:.1f}% exceeds maximum {criteria['lvr_limits'][loan_purpose]['with_lmi']}%")
        
        # Check DTI limits
        dti_key = f"{loan_purpose}_under_80" if lvr <= 80 else "80_to_90_lvr" if lvr <= 90 else "above_90_lvr"
        max_dti = criteria["dti_limits"][dti_key]
        
        if dti <= max_dti:
            reasons.append(f"DTI {dti:.1f} within limit of {max_dti}")
        else:
            eligible = False
            score -= 30
            warnings.append(f"DTI {dti:.1f} exceeds maximum {max_dti}")
        
        # Check minimum income
        employment_key = "payg" if client.employment_type in [EmploymentType.PAYG_PERMANENT, EmploymentType.PAYG_CASUAL] else "self_employed"
        min_income = criteria["min_income"][employment_key]
        
        if client.annual_income >= min_income:
            reasons.append(f"Income ${client.annual_income:,} meets minimum ${min_income:,}")
        else:
            eligible = False
            score -= 40
            warnings.append(f"Income ${client.annual_income:,} below minimum ${min_income:,}")
        
        # Check employment requirements
        emp_req_map = {
            EmploymentType.PAYG_PERMANENT: "payg_permanent",
            EmploymentType.PAYG_CASUAL: "payg_casual", 
            EmploymentType.SELF_EMPLOYED: "self_employed",
            EmploymentType.CONTRACT: "contract"
        }
        
        req_period = criteria["employment_requirements"][emp_req_map[client.employment_type]]
        months_required = int(req_period.split("_")[0]) if "_months" in req_period else int(req_period.split("_")[0]) * 12
        
        if client.employment_months >= months_required:
            reasons.append(f"Employment history {client.employment_months} months sufficient")
        else:
            score -= 20
            warnings.append(f"Employment history {client.employment_months} months below required {months_required}")
        
        # Determine interest rate
        rate_key = f"{loan_purpose}_pi"  # Assuming Principal & Interest
        interest_rate = criteria["interest_rates"][rate_key]
        
        return LenderMatch(
            lender_name="Great Southern Bank",
            eligible=eligible,
            match_score=max(0, score),
            reasons=reasons,
            warnings=warnings,
            interest_rate=interest_rate
        )
    
    def match_latrobe_financial(self, client: ClientProfile) -> LenderMatch:
        """Match client against LaTrobe Financial criteria"""
        criteria = self.criteria["lenders"]["latrobe_financial"]
        
        eligible = True
        reasons = []
        warnings = []
        score = 100
        
        # Check loan amount limits
        if client.loan_amount < criteria["loan_amount"]["minimum"]:
            eligible = False
            score -= 50
            warnings.append(f"Loan amount ${client.loan_amount:,} below minimum ${criteria['loan_amount']['minimum']:,}")
        elif client.loan_amount > criteria["loan_amount"]["maximum"]:
            eligible = False
            score -= 50
            warnings.append(f"Loan amount ${client.loan_amount:,} exceeds maximum ${criteria['loan_amount']['maximum']:,}")
        else:
            reasons.append("Loan amount within acceptable range")
        
        # Check LVR based on loan amount
        lvr = self.calculate_lvr(client.loan_amount, client.property_value)
        
        if client.loan_amount <= 3000000:
            max_lvr = criteria["lvr_limits"]["all_purposes"]["up_to_3m"]
        elif client.loan_amount <= 5000000:
            max_lvr = criteria["lvr_limits"]["all_purposes"]["3m_to_5m"]
        else:
            max_lvr = criteria["lvr_limits"]["all_purposes"]["5m_to_25m"]
        
        if lvr <= max_lvr:
            reasons.append(f"LVR {lvr:.1f}% within {max_lvr}% limit for loan size")
        else:
            eligible = False
            score -= 40
            warnings.append(f"LVR {lvr:.1f}% exceeds {max_lvr}% limit for loan amount ${client.loan_amount:,}")
        
        # LaTrobe specializes in "life event" lending - bonus for lower credit scores
        if client.credit_score < 650:
            score += 10
            reasons.append("Specialist in life event lending - suitable for credit-impaired borrowers")
        
        # Estimate interest rate (higher than banks due to risk)
        base_rate = 6.5  # Typical non-bank rate
        if client.credit_score < 650:
            base_rate += 0.5
        
        return LenderMatch(
            lender_name="LaTrobe Financial",
            eligible=eligible,
            match_score=max(0, score),
            reasons=reasons,
            warnings=warnings,
            interest_rate=base_rate
        )
    
    def match_suncorp_bank(self, client: ClientProfile) -> LenderMatch:
        """Match client against Suncorp Bank criteria"""
        criteria = self.criteria["lenders"]["suncorp_bank"]
        
        eligible = True
        reasons = []
        warnings = []
        score = 100
        
        # Check basic LVR
        lvr = self.calculate_lvr(client.loan_amount, client.property_value)
        max_lvr = criteria["lvr_limits"]["maximum"]
        
        if lvr <= max_lvr:
            reasons.append(f"LVR {lvr:.1f}% within maximum {max_lvr}%")
        else:
            eligible = False
            score -= 50
            warnings.append(f"LVR {lvr:.1f}% exceeds maximum {max_lvr}%")
        
        # Check employment requirements based on type
        if client.employment_type == EmploymentType.PAYG_PERMANENT:
            req_months = 3
            if client.employment_months >= req_months:
                reasons.append("PAYG permanent employment meets 3-month requirement")
            else:
                score -= 20
                warnings.append(f"PAYG permanent employment {client.employment_months} months below 3-month requirement")
        
        elif client.employment_type == EmploymentType.PAYG_CASUAL:
            req_months = 6
            if client.employment_months >= req_months:
                reasons.append("Casual employment meets 6-month requirement")
            else:
                score -= 25
                warnings.append(f"Casual employment {client.employment_months} months below 6-month requirement")
        
        elif client.employment_type == EmploymentType.SELF_EMPLOYED:
            req_months = 24
            if client.employment_months >= req_months:
                reasons.append("Self-employed meets 2-year trading requirement")
            else:
                eligible = False
                score -= 40
                warnings.append(f"Self-employed trading {client.employment_months} months below 24-month requirement")
        
        # Check genuine savings if high LVR
        deposit_percentage = (client.deposit / client.property_value) * 100
        if lvr > 90:
            required_savings = criteria["genuine_savings"]["minimum_percentage"]
            if deposit_percentage >= required_savings:
                reasons.append(f"Genuine savings {deposit_percentage:.1f}% meets {required_savings}% requirement")
            else:
                eligible = False
                score -= 30
                warnings.append(f"Genuine savings {deposit_percentage:.1f}% below {required_savings}% requirement for LVR >90%")
        
        # Estimate competitive bank rate
        interest_rate = 5.95 if client.first_home_buyer else 6.25
        
        return LenderMatch(
            lender_name="Suncorp Bank",
            eligible=eligible,
            match_score=max(0, score),
            reasons=reasons,
            warnings=warnings,
            interest_rate=interest_rate
        )
    
    def match_all_lenders(self, client: ClientProfile) -> List[LenderMatch]:
        """Match client against all lenders and return ranked results"""
        matches = [
            self.match_great_southern_bank(client),
            self.match_latrobe_financial(client), 
            self.match_suncorp_bank(client)
        ]
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Only return eligible matches with score > 50
        return [match for match in matches if match.eligible and match.match_score > 50]

# Example usage
def test_matching_engine():
    """Test the matching engine with sample data"""
    
    # Create a sample client profile
    client = ClientProfile(
        annual_income=85000,
        loan_amount=450000,
        property_value=550000,
        property_type=PropertyType.HOUSE,
        employment_type=EmploymentType.PAYG_PERMANENT,
        employment_months=18,
        deposit=100000,
        existing_debts=15000,
        credit_score=720,
        first_home_buyer=True
    )
    
    # Initialize matching engine
    engine = LenderMatchingEngine()
    
    # Get matches
    matches = engine.match_all_lenders(client)
    
    print(f"Found {len(matches)} suitable lenders for client:")
    print(f"Income: ${client.annual_income:,}, Loan: ${client.loan_amount:,}, LVR: {engine.calculate_lvr(client.loan_amount, client.property_value):.1f}%")
    print()
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.lender_name}")
        print(f"   Match Score: {match.match_score}%")
        print(f"   Interest Rate: {match.interest_rate}%")
        print(f"   Reasons: {'; '.join(match.reasons)}")
        if match.warnings:
            print(f"   Warnings: {'; '.join(match.warnings)}")
        print()

if __name__ == "__main__":
    test_matching_engine()