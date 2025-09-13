#!/usr/bin/env python3
"""
Serviceability Calculator - Income minus expenses with buffers + LVR Calculator
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

@dataclass
class ServiceabilityResult:
    can_service: bool
    monthly_capacity: float
    ndi_ratio: float
    dti_ratio: float
    buffer_used: float
    warnings: List[str]
    recommendations: List[str]

@dataclass
class LVRResult:
    lvr: float
    deposit_required: float
    lmi_required: bool
    lmi_premium: float
    max_loan_amount: float
    warnings: List[str]

class ServiceabilityCalculator:
    
    def __init__(self):
        # Interest rate buffers (add to actual rate for serviceability)
        self.serviceability_buffers = {
            "great_southern_bank": 3.0,  # 3% buffer
            "suncorp_bank": 2.5,         # 2.5% buffer  
            "latrobe_financial": 2.0,     # 2% buffer (non-bank)
            "default": 2.5
        }
        
        # Household Expenditure Measure (HEM) - minimum living expenses
        self.hem_benchmarks = {
            "single_no_dependents": 2500,
            "couple_no_dependents": 3500,
            "single_1_dependent": 3200,
            "couple_1_dependent": 4200,
            "single_2_dependents": 3800,
            "couple_2_dependents": 4800,
            "single_3_dependents": 4400,
            "couple_3_dependents": 5400
        }
        
        # LMI premium rates (approximate)
        self.lmi_rates = {
            85: 0.89,  # LVR 85% = 0.89% of loan amount
            90: 1.86,  # LVR 90% = 1.86% of loan amount  
            95: 3.94   # LVR 95% = 3.94% of loan amount
        }
    
    def calculate_serviceability(self, 
                               gross_annual_income: float,
                               monthly_expenses: float,
                               existing_monthly_debts: float,
                               proposed_loan_amount: float,
                               interest_rate: float,
                               loan_term_years: int = 30,
                               lender: str = "default",
                               dependents: int = 0,
                               is_couple: bool = False) -> ServiceabilityResult:
        """Calculate if borrower can service the proposed loan"""
        
        warnings = []
        recommendations = []
        
        # Apply serviceability buffer to interest rate
        buffer = self.serviceability_buffers.get(lender, self.serviceability_buffers["default"])
        buffered_rate = (interest_rate + buffer) / 100
        
        # Calculate monthly payment at buffered rate
        monthly_payment = self._calculate_monthly_payment(
            proposed_loan_amount, buffered_rate, loan_term_years
        )
        
        # Calculate net income (after tax)
        monthly_gross = gross_annual_income / 12
        monthly_net = self._calculate_net_income(gross_annual_income) / 12
        
        # Check expenses against HEM benchmark
        hem_category = self._get_hem_category(is_couple, dependents)
        hem_minimum = self.hem_benchmarks[hem_category]
        
        if monthly_expenses < hem_minimum:
            warnings.append(f"Declared expenses ${monthly_expenses:,.0f} below HEM benchmark ${hem_minimum:,.0f}")
            monthly_expenses = max(monthly_expenses, hem_minimum)
        
        # Calculate total monthly commitments
        total_monthly_commitments = monthly_expenses + existing_monthly_debts + monthly_payment
        
        # Calculate Net Disposable Income (NDI)
        ndi = monthly_net - total_monthly_commitments
        ndi_ratio = ndi / monthly_payment if monthly_payment > 0 else 0
        
        # Calculate Debt-to-Income ratio
        total_debt = proposed_loan_amount + (existing_monthly_debts * 12 / 0.05)  # Estimate existing debt balance
        dti_ratio = total_debt / gross_annual_income
        
        # Serviceability assessment
        can_service = ndi >= 0 and ndi_ratio >= 0.1  # Need 10% buffer minimum
        
        # Generate warnings and recommendations
        if ndi < 0:
            warnings.append("Negative Net Disposable Income - cannot service loan")
        elif ndi_ratio < 0.2:
            warnings.append("Low serviceability buffer - may be declined by lenders")
        elif ndi_ratio < 0.5:
            warnings.append("Moderate serviceability risk")
        
        if dti_ratio > 6:
            warnings.append(f"High DTI ratio {dti_ratio:.1f}x - may exceed lender limits")
        elif dti_ratio > 5:
            warnings.append(f"Elevated DTI ratio {dti_ratio:.1f}x - some lender restrictions may apply")
        
        # Recommendations
        if not can_service:
            recommendations.append("Consider reducing loan amount or extending loan term")
            recommendations.append("Review and reduce monthly expenses where possible")
            recommendations.append("Consider paying down existing debts before applying")
        
        if dti_ratio > 6:
            recommendations.append("Consider reducing loan amount to improve DTI ratio")
        
        return ServiceabilityResult(
            can_service=can_service,
            monthly_capacity=ndi,
            ndi_ratio=ndi_ratio,
            dti_ratio=dti_ratio,
            buffer_used=buffer,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def calculate_lvr_and_lmi(self,
                             loan_amount: float,
                             property_value: float,
                             lender: str = "default") -> LVRResult:
        """Calculate LVR and determine LMI requirements"""
        
        warnings = []
        
        # Calculate LVR
        lvr = (loan_amount / property_value) * 100
        deposit_amount = property_value - loan_amount
        deposit_percentage = (deposit_amount / property_value) * 100
        
        # Determine if LMI is required (typically >80% LVR)
        lmi_required = lvr > 80
        lmi_premium = 0.0
        
        if lmi_required:
            # Estimate LMI premium based on LVR
            if lvr <= 85:
                lmi_rate = self.lmi_rates[85]
            elif lvr <= 90:
                lmi_rate = self.lmi_rates[90]
            elif lvr <= 95:
                lmi_rate = self.lmi_rates[95]
            else:
                warnings.append("LVR exceeds 95% - may not be acceptable to most lenders")
                lmi_rate = self.lmi_rates[95]
            
            lmi_premium = loan_amount * (lmi_rate / 100)
        
        # Lender-specific LVR limits
        max_loan_amount = self._get_max_loan_amount(property_value, lender)
        
        # LVR assessment warnings
        if lvr > 95:
            warnings.append("LVR exceeds 95% - very limited lender options")
        elif lvr > 90:
            warnings.append("LVR exceeds 90% - may require genuine savings verification")
        elif lvr > 80:
            warnings.append("LVR exceeds 80% - Lenders Mortgage Insurance required")
        
        if deposit_percentage < 5:
            warnings.append("Deposit less than 5% - genuine savings may be required")
        
        return LVRResult(
            lvr=lvr,
            deposit_required=deposit_amount,
            lmi_required=lmi_required,
            lmi_premium=lmi_premium,
            max_loan_amount=max_loan_amount,
            warnings=warnings
        )
    
    def calculate_maximum_borrowing_capacity(self,
                                           gross_annual_income: float,
                                           monthly_expenses: float,
                                           existing_monthly_debts: float,
                                           interest_rate: float,
                                           loan_term_years: int = 30,
                                           lender: str = "default") -> float:
        """Calculate maximum amount borrower can borrow"""
        
        # Apply serviceability buffer
        buffer = self.serviceability_buffers.get(lender, self.serviceability_buffers["default"])
        buffered_rate = (interest_rate + buffer) / 100
        
        # Calculate available monthly income for loan repayment
        monthly_net = self._calculate_net_income(gross_annual_income) / 12
        available_for_loan = monthly_net - monthly_expenses - existing_monthly_debts
        
        # Ensure minimum buffer
        available_for_loan *= 0.9  # Keep 10% buffer
        
        if available_for_loan <= 0:
            return 0
        
        # Calculate maximum loan amount based on available payment capacity
        max_loan = self._calculate_loan_amount_from_payment(
            available_for_loan, buffered_rate, loan_term_years
        )
        
        return max_loan
    
    def _calculate_monthly_payment(self, loan_amount: float, annual_rate: float, years: int) -> float:
        """Calculate monthly P&I payment"""
        if annual_rate == 0:
            return loan_amount / (years * 12)
        
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                 ((1 + monthly_rate)**num_payments - 1)
        
        return payment
    
    def _calculate_loan_amount_from_payment(self, payment: float, annual_rate: float, years: int) -> float:
        """Calculate loan amount from desired monthly payment"""
        if annual_rate == 0:
            return payment * years * 12
        
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        loan_amount = payment * ((1 + monthly_rate)**num_payments - 1) / \
                     (monthly_rate * (1 + monthly_rate)**num_payments)
        
        return loan_amount
    
    def _calculate_net_income(self, gross_annual: float) -> float:
        """Simple net income calculation after tax"""
        # Simplified Australian tax calculation
        if gross_annual <= 18200:
            tax = 0
        elif gross_annual <= 45000:
            tax = (gross_annual - 18200) * 0.19
        elif gross_annual <= 120000:
            tax = 5092 + (gross_annual - 45000) * 0.325
        elif gross_annual <= 180000:
            tax = 29467 + (gross_annual - 120000) * 0.37
        else:
            tax = 51667 + (gross_annual - 180000) * 0.45
        
        return gross_annual - tax
    
    def _get_hem_category(self, is_couple: bool, dependents: int) -> str:
        """Get HEM category based on family structure"""
        couple_prefix = "couple" if is_couple else "single"
        
        if dependents == 0:
            return f"{couple_prefix}_no_dependents"
        elif dependents == 1:
            return f"{couple_prefix}_1_dependent"
        elif dependents == 2:
            return f"{couple_prefix}_2_dependents"
        else:
            return f"{couple_prefix}_3_dependents"  # 3+ dependents
    
    def _get_max_loan_amount(self, property_value: float, lender: str) -> float:
        """Get maximum loan amount based on lender LVR limits"""
        # Standard LVR limits by lender
        max_lvr = {
            "great_southern_bank": 95,
            "suncorp_bank": 95,
            "latrobe_financial": 80,  # Conservative non-bank
            "default": 95
        }
        
        lvr_limit = max_lvr.get(lender, max_lvr["default"])
        return property_value * (lvr_limit / 100)

# Example usage and testing
def test_serviceability_calculator():
    """Test the serviceability calculation system"""
    
    calculator = ServiceabilityCalculator()
    
    # Test case
    gross_income = 85000
    monthly_expenses = 3500
    existing_debts = 800
    loan_amount = 450000
    property_value = 550000
    interest_rate = 6.0
    
    print("Serviceability Analysis:")
    print(f"Income: ${gross_income:,}")
    print(f"Loan Amount: ${loan_amount:,}")
    print(f"Property Value: ${property_value:,}")
    print()
    
    # Test serviceability
    serviceability = calculator.calculate_serviceability(
        gross_income, monthly_expenses, existing_debts, 
        loan_amount, interest_rate, lender="great_southern_bank"
    )
    
    print("Serviceability Results:")
    print(f"Can Service: {serviceability.can_service}")
    print(f"Monthly Capacity: ${serviceability.monthly_capacity:,.2f}")
    print(f"NDI Ratio: {serviceability.ndi_ratio:.2f}")
    print(f"DTI Ratio: {serviceability.dti_ratio:.1f}x")
    print(f"Buffer Used: {serviceability.buffer_used}%")
    print()
    
    if serviceability.warnings:
        print("Warnings:")
        for warning in serviceability.warnings:
            print(f"  • {warning}")
        print()
    
    # Test LVR calculation
    lvr_result = calculator.calculate_lvr_and_lmi(loan_amount, property_value)
    
    print("LVR Analysis:")
    print(f"LVR: {lvr_result.lvr:.1f}%")
    print(f"Deposit Required: ${lvr_result.deposit_required:,.0f}")
    print(f"LMI Required: {lvr_result.lmi_required}")
    if lvr_result.lmi_required:
        print(f"LMI Premium: ${lvr_result.lmi_premium:,.0f}")
    print()
    
    # Test maximum borrowing capacity
    max_capacity = calculator.calculate_maximum_borrowing_capacity(
        gross_income, monthly_expenses, existing_debts, interest_rate
    )
    
    print(f"Maximum Borrowing Capacity: ${max_capacity:,.0f}")

if __name__ == "__main__":
    test_serviceability_calculator()