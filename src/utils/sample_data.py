"""
Sample data generator for testing the loan recommendation system
"""
import os
import json
from pathlib import Path

def create_sample_bank_documents():
    """Create sample bank documents for testing"""
    
    sample_docs_dir = Path("./data/raw")
    sample_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample CommBank loan products
    commbank_content = """
    COMMONWEALTH BANK HOME LOANS - PRODUCT GUIDE 2024
    
    VARIABLE RATE HOME LOANS
    
    1. STREAMLINE BASIC HOME LOAN
    - Interest Rate: 6.24% p.a.
    - Comparison Rate: 6.25% p.a.
    - Application Fee: $600
    - No ongoing fees
    - Minimum Loan: $150,000
    - Maximum Loan: $3,000,000
    - Maximum LVR: 95%
    - Features: Online redraw, extra repayments allowed
    - Minimum Income: $80,000 p.a.
    - Suitable for: Owner occupiers, investors
    - Self-employed accepted with 2 years tax returns
    
    2. WEALTH PACKAGE HOME LOAN  
    - Interest Rate: 6.04% p.a.
    - Comparison Rate: 6.12% p.a.
    - Application Fee: $600
    - Package Fee: $395 annually
    - Minimum Loan: $150,000
    - Maximum LVR: 95%
    - Features: 100% offset account, unlimited extra repayments, redraw facility
    - Minimum Income: $150,000 p.a.
    - Premium banking benefits included
    
    FIRST HOME BUYER SPECIALS
    
    3. FIRST HOME BUYER LOAN
    - Interest Rate: 5.89% p.a. (1 year introductory)
    - Then reverts to: 6.24% p.a.
    - Comparison Rate: 6.18% p.a.
    - No application fee for qualified FHB
    - Maximum LVR: 95% (no LMI with 10% deposit for eligible properties)
    - Minimum Income: $60,000 p.a.
    - Employment: Minimum 3 months current employment
    - Available for properties up to $750,000
    
    ELIGIBILITY CRITERIA:
    - Australian citizens or permanent residents
    - Minimum age: 18 years
    - Stable employment history
    - Satisfactory credit history
    - Property must be in metropolitan areas
    - Mortgage insurance required for LVR > 80%
    """
    
    # Sample ANZ loan products
    anz_content = """
    ANZ HOME LOANS - RATE SHEET 2024
    
    VARIABLE RATE PRODUCTS
    
    1. ANZ SIMPLICITY PLUS
    - Variable Rate: 6.19% p.a.
    - Comparison Rate: 6.20% p.a.
    - Application Fee: $799
    - Monthly Fee: $10
    - Loan Range: $80,000 - $2,000,000
    - Max LVR: 90% (95% with suitable deposit source)
    - Features: Offset account, redraw, extra repayments
    - Min Income: $50,000 individual, $80,000 joint
    
    2. ANZ BREAKFREE PACKAGE
    - Variable Rate: 5.94% p.a.
    - Comparison Rate: 6.08% p.a.
    - Application Fee: $799
    - Annual Package Fee: $395
    - Premium features: Multiple offset accounts, fee waivers
    - Maximum LVR: 95%
    - Minimum loan: $250,000
    - Suitable for high-income earners ($100,000+)
    
    FIXED RATE OPTIONS
    
    3. ANZ 2-YEAR FIXED
    - Fixed Rate: 5.79% p.a.
    - Comparison Rate: 6.15% p.a.
    - Fix period: 2 years
    - Then variable: 6.19% p.a.
    - Same fees as Simplicity Plus
    
    INVESTMENT PROPERTY LOANS
    - Additional 0.25% margin on all rates
    - Maximum LVR: 90%
    - Minimum deposit: 20%
    - Rental income assessed at 75%
    
    SELF-EMPLOYED CRITERIA:
    - 2 years ABN registration
    - Recent tax returns and BAS statements
    - Accountant verification letter
    - Additional 0.15% rate loading may apply
    
    EMPLOYMENT REQUIREMENTS:
    - Permanent: 3 months current role
    - Contract: 6 months remaining, history of renewals
    - Casual: 12 months same employer
    - Probation acceptable with employment contract
    """
    
    # Sample Westpac loan products  
    westpac_content = """
    WESTPAC HOME LENDING - PRODUCT DISCLOSURE 2024
    
    PREMIER ADVANTAGE PACKAGE
    
    1. VARIABLE RATE LOAN
    - Interest Rate: 6.09% p.a.
    - Comparison Rate: 6.18% p.a.
    - Annual Package Fee: $395
    - No application fee
    - Loan Amount: $150,000 - $5,000,000
    - LVR up to 95%
    - Features: Offset accounts, redraw, no extra repayment restrictions
    
    BASIC HOME LOAN
    
    2. WESTPAC BASIC VARIABLE
    - Interest Rate: 6.34% p.a.
    - Comparison Rate: 6.36% p.a.
    - Application Fee: $599
    - No ongoing fees
    - Basic features only
    - Maximum LVR: 90%
    - Minimum loan: $50,000
    
    FIRST HOME BUYER SUPPORT
    
    3. FIRST HOME COACH LOAN
    - Special rate: 5.84% p.a. (first 12 months)
    - Then standard variable: 6.09% p.a.
    - Comparison Rate: 6.04% p.a.
    - $0 application fee
    - Up to 95% LVR
    - Dedicated first home buyer support
    - Eligible for government grants
    - Property value up to $800,000
    
    ELIGIBILITY STANDARDS:
    - Minimum income: $40,000 (single), $60,000 (joint)
    - Credit score: Minimum 600
    - Employment: 6 months continuous (3 months for permanent)
    - Age: 18-65 years
    - Deposit: Minimum 5% genuine savings (10% for investment)
    
    PROPERTY TYPES ACCEPTED:
    - Houses, apartments, townhouses
    - New and established properties
    - Off-the-plan purchases (with conditions)
    - Investment properties (additional criteria apply)
    
    SERVICEABILITY ASSESSMENT:
    - Income verification required
    - Debt-to-income ratio maximum 6:1
    - Living expenses assessed
    - Interest rate buffer: 3.0%
    """
    
    # Write sample documents
    with open(sample_docs_dir / "commbank_home_loans.txt", "w") as f:
        f.write(commbank_content)
    
    with open(sample_docs_dir / "anz_home_loans.txt", "w") as f:
        f.write(anz_content)
    
    with open(sample_docs_dir / "westpac_home_loans.txt", "w") as f:
        f.write(westpac_content)
    
    print(f"Created sample bank documents in {sample_docs_dir}")

def create_sample_client_profiles():
    """Create sample client profiles for testing"""
    
    sample_clients = [
        {
            "name": "First Home Buyer - Young Professional",
            "annual_income": 95000,
            "savings": 85000,
            "loan_amount": 500000,
            "property_value": 580000,
            "property_type": "apartment",
            "employment_type": "full_time",
            "employment_length_months": 18,
            "credit_score": 750,
            "existing_debts": 15000,
            "dependents": 0,
            "first_home_buyer": True
        },
        {
            "name": "Family Upgrade - High Income",
            "annual_income": 180000,
            "savings": 150000,
            "loan_amount": 750000,
            "property_value": 900000,
            "property_type": "house",
            "employment_type": "full_time", 
            "employment_length_months": 48,
            "credit_score": 800,
            "existing_debts": 25000,
            "dependents": 2,
            "first_home_buyer": False
        },
        {
            "name": "Self-Employed Investor",
            "annual_income": 120000,
            "savings": 200000,
            "loan_amount": 400000,
            "property_value": 500000,
            "property_type": "investment",
            "employment_type": "self_employed",
            "employment_length_months": 36,
            "credit_score": 720,
            "existing_debts": 50000,
            "dependents": 1,
            "first_home_buyer": False
        }
    ]
    
    test_data_dir = Path("./data/test_profiles")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    with open(test_data_dir / "sample_clients.json", "w") as f:
        json.dump(sample_clients, f, indent=2)
    
    print(f"Created sample client profiles in {test_data_dir}")

if __name__ == "__main__":
    create_sample_bank_documents()
    create_sample_client_profiles()