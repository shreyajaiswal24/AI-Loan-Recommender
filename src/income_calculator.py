#!/usr/bin/env python3
"""
Income Calculator - Handles multiple employment types with correct percentages
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

class IncomeType(Enum):
    PAYG_PERMANENT = "payg_permanent"
    PAYG_CASUAL = "payg_casual"
    PAYG_CONTRACT = "payg_contract"
    SELF_EMPLOYED = "self_employed"
    RENTAL_INCOME = "rental_income"
    OVERTIME = "overtime"
    BONUS = "bonus"
    COMMISSION = "commission"
    PENSION = "pension"
    GOVERNMENT_BENEFITS = "government_benefits"
    FOREIGN_INCOME = "foreign_income"

@dataclass
class IncomeSource:
    income_type: IncomeType
    gross_amount: float
    frequency: str  # "weekly", "monthly", "annually"
    employment_months: int = 0
    is_essential_worker: bool = False
    currency: str = "AUD"

@dataclass
class IncomeCalculationResult:
    total_usable_income: float
    breakdown: Dict[str, float]
    warnings: List[str]
    employment_stability_score: float

class IncomeCalculator:
    
    def __init__(self):
        # Income percentage multipliers based on lending policies
        self.income_multipliers = {
            IncomeType.PAYG_PERMANENT: 1.00,
            IncomeType.PAYG_CASUAL: 1.00,
            IncomeType.PAYG_CONTRACT: 1.00,
            IncomeType.SELF_EMPLOYED: 1.00,
            IncomeType.RENTAL_INCOME: 0.75,  # 75% after expenses/vacancy
            IncomeType.OVERTIME: {
                "essential_worker": 1.00,
                "non_essential": 0.80
            },
            IncomeType.BONUS: 0.80,
            IncomeType.COMMISSION: 0.80,
            IncomeType.PENSION: 1.00,
            IncomeType.GOVERNMENT_BENEFITS: 1.00,
            IncomeType.FOREIGN_INCOME: 0.70  # 70% due to currency risk
        }
        
        # Minimum employment periods (months)
        self.min_employment_periods = {
            IncomeType.PAYG_PERMANENT: 3,
            IncomeType.PAYG_CASUAL: 6,
            IncomeType.PAYG_CONTRACT: 6,
            IncomeType.SELF_EMPLOYED: 24,
            IncomeType.OVERTIME: 6,
            IncomeType.BONUS: 24,
            IncomeType.COMMISSION: 6,
        }
    
    def annualize_income(self, amount: float, frequency: str) -> float:
        """Convert income to annual amount"""
        if frequency == "weekly":
            return amount * 52
        elif frequency == "fortnightly":
            return amount * 26
        elif frequency == "monthly":
            return amount * 12
        elif frequency == "annually":
            return amount
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
    
    def calculate_usable_income(self, income_sources: List[IncomeSource]) -> IncomeCalculationResult:
        """Calculate total usable income from all sources"""
        
        total_usable = 0.0
        breakdown = {}
        warnings = []
        employment_stability = 100.0
        
        for source in income_sources:
            annual_gross = self.annualize_income(source.gross_amount, source.frequency)
            
            # Check minimum employment period
            min_period = self.min_employment_periods.get(source.income_type, 0)
            if source.employment_months < min_period:
                warnings.append(f"{source.income_type.value}: {source.employment_months} months below minimum {min_period} months")
                employment_stability -= 15
                continue  # Skip this income source
            
            # Apply income multipliers
            if source.income_type == IncomeType.OVERTIME:
                multiplier = self.income_multipliers[source.income_type]["essential_worker"] if source.is_essential_worker else self.income_multipliers[source.income_type]["non_essential"]
            else:
                multiplier = self.income_multipliers[source.income_type]
            
            usable_income = annual_gross * multiplier
            
            # Special handling for foreign income
            if source.income_type == IncomeType.FOREIGN_INCOME:
                if source.currency not in ["USD", "GBP", "EUR", "NZD", "SGD", "CAD", "HKD", "JPY"]:
                    warnings.append(f"Foreign currency {source.currency} may not be acceptable")
                    continue
                warnings.append(f"Foreign income converted at 70% to account for currency risk")
            
            # Self-employed income stability check
            if source.income_type == IncomeType.SELF_EMPLOYED:
                if source.employment_months < 36:  # Less than 3 years
                    employment_stability -= 10
                    warnings.append("Self-employed less than 3 years - may require additional documentation")
            
            # Casual employment stability
            if source.income_type == IncomeType.PAYG_CASUAL:
                employment_stability -= 5
                warnings.append("Casual employment may be viewed as less stable by lenders")
            
            total_usable += usable_income
            breakdown[f"{source.income_type.value}_{source.frequency}"] = usable_income
        
        return IncomeCalculationResult(
            total_usable_income=total_usable,
            breakdown=breakdown,
            warnings=warnings,
            employment_stability_score=max(0, employment_stability)
        )
    
    def calculate_net_disposable_income(self, gross_income: float, expenses: float, 
                                      existing_debts: float, proposed_repayment: float) -> Dict:
        """Calculate Net Disposable Income (NDI) for serviceability"""
        
        # Estimate tax (simplified calculation)
        estimated_tax = self._calculate_income_tax(gross_income)
        net_income = gross_income - estimated_tax
        
        # Calculate NDI
        total_expenses = expenses + existing_debts + proposed_repayment
        ndi = net_income - total_expenses
        
        # NDI ratio (should be positive, ideally >1.0 for buffer)
        ndi_ratio = ndi / proposed_repayment if proposed_repayment > 0 else 0
        
        return {
            "gross_income": gross_income,
            "estimated_tax": estimated_tax,
            "net_income": net_income,
            "total_expenses": total_expenses,
            "net_disposable_income": ndi,
            "ndi_ratio": ndi_ratio,
            "assessment": "Positive" if ndi > 0 else "Negative"
        }
    
    def _calculate_income_tax(self, annual_income: float) -> float:
        """Simplified Australian tax calculation"""
        # 2024 tax brackets (simplified)
        if annual_income <= 18200:
            return 0
        elif annual_income <= 45000:
            return (annual_income - 18200) * 0.19
        elif annual_income <= 120000:
            return 5092 + (annual_income - 45000) * 0.325
        elif annual_income <= 180000:
            return 29467 + (annual_income - 120000) * 0.37
        else:
            return 51667 + (annual_income - 180000) * 0.45
    
    def validate_income_documentation(self, income_sources: List[IncomeSource]) -> Dict:
        """Check what documentation is required for income verification"""
        
        documentation_required = {}
        
        for source in income_sources:
            docs = []
            
            if source.income_type == IncomeType.PAYG_PERMANENT:
                docs = ["Recent payslip (3 months YTD)", "Employment letter or contract"]
            
            elif source.income_type == IncomeType.PAYG_CASUAL:
                docs = ["Recent payslip (6 months YTD)", "Employment letter confirming regular hours"]
            
            elif source.income_type == IncomeType.SELF_EMPLOYED:
                docs = ["2 years tax returns", "2 years financial statements", "Accountant's letter", "BAS statements"]
            
            elif source.income_type == IncomeType.RENTAL_INCOME:
                docs = ["Lease agreement", "Property manager statement", "Tax return (rental schedule)"]
            
            elif source.income_type == IncomeType.BONUS:
                docs = ["Payslips showing bonus (2 years)", "Employment letter confirming bonus structure"]
            
            elif source.income_type == IncomeType.PENSION:
                docs = ["Centrelink statement", "Bank statements showing payments"]
            
            elif source.income_type == IncomeType.FOREIGN_INCOME:
                docs = ["Employment contract", "Bank statements (6 months)", "Certified English translation"]
            
            documentation_required[source.income_type.value] = docs
        
        return documentation_required

# Example usage and testing
def test_income_calculator():
    """Test the income calculation system"""
    
    calculator = IncomeCalculator()
    
    # Test case: Mixed income sources
    income_sources = [
        IncomeSource(
            income_type=IncomeType.PAYG_PERMANENT,
            gross_amount=1500,  # per week
            frequency="weekly",
            employment_months=18
        ),
        IncomeSource(
            income_type=IncomeType.RENTAL_INCOME,
            gross_amount=2000,  # per month
            frequency="monthly",
            employment_months=12
        ),
        IncomeSource(
            income_type=IncomeType.OVERTIME,
            gross_amount=200,  # per week
            frequency="weekly",
            employment_months=18,
            is_essential_worker=False
        )
    ]
    
    # Calculate income
    result = calculator.calculate_usable_income(income_sources)
    
    print("Income Calculation Results:")
    print(f"Total Usable Income: ${result.total_usable_income:,.2f}")
    print(f"Employment Stability Score: {result.employment_stability_score}%")
    print()
    
    print("Income Breakdown:")
    for source, amount in result.breakdown.items():
        print(f"  {source}: ${amount:,.2f}")
    print()
    
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  • {warning}")
        print()
    
    # Test serviceability
    expenses = 4000  # Monthly
    existing_debts = 800  # Monthly
    proposed_repayment = 2500  # Monthly
    
    monthly_income = result.total_usable_income / 12
    ndi_result = calculator.calculate_net_disposable_income(
        result.total_usable_income, 
        expenses * 12, 
        existing_debts * 12, 
        proposed_repayment * 12
    )
    
    print("Serviceability Assessment:")
    print(f"Monthly Gross Income: ${monthly_income:,.2f}")
    print(f"Monthly Net Income: ${ndi_result['net_income']/12:,.2f}")
    print(f"Monthly NDI: ${ndi_result['net_disposable_income']/12:,.2f}")
    print(f"NDI Ratio: {ndi_result['ndi_ratio']:.2f}")
    print(f"Assessment: {ndi_result['assessment']}")
    print()
    
    # Documentation requirements
    docs = calculator.validate_income_documentation(income_sources)
    print("Required Documentation:")
    for income_type, doc_list in docs.items():
        print(f"  {income_type}:")
        for doc in doc_list:
            print(f"    • {doc}")

if __name__ == "__main__":
    test_income_calculator()