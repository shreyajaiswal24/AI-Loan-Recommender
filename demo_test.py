#!/usr/bin/env python3
"""
Quick test of the running AI Loan Recommendation System
"""
import requests
import json
import time

def test_recommendation_system():
    """Test the loan recommendation system"""
    
    # Test different client scenarios
    test_scenarios = [
        {
            "name": "First Home Buyer - Young Professional",
            "profile": {
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
            }
        },
        {
            "name": "Family Upgrade - High Income",
            "profile": {
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
            }
        },
        {
            "name": "Investment Property - Self-Employed",
            "profile": {
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
        }
    ]
    
    print("AI Loan Recommendation System - Live Demo")
    print("=" * 60)
    print("Server running at: http://localhost:8000")
    print("Testing different client scenarios...")
    print()
    
    for scenario in test_scenarios:
        print(f"Testing: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/demo-recommend",
                json=scenario["profile"],
                timeout=10
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                client = data["client_summary"]
                
                print(f"Success in {processing_time:.2f}s")
                print(f"Profile: ${client['income']:,} income, {client['lvr']}% LVR, {client['deposit']}% deposit")
                print(f"Found {len(data['recommendations'])} recommendations:")
                print()
                
                for i, rec in enumerate(data["recommendations"], 1):
                    loan = rec["loan_product"]
                    emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "🏅"
                    
                    print(f"  {emoji} #{i} - {loan['bank_name']} {loan['product_name']}")
                    print(f"      Rate: {loan['interest_rate']}% | Monthly: ${rec['estimated_monthly_payment']:,.2f}")
                    print(f"      Score: {rec['match_score']}% | Fee: ${loan['application_fee']}")
                    print(f"      Why: {rec['reasoning']}")
                    if rec['warnings']:
                        print(f"        {', '.join(rec['warnings'])}")
                    print()
                
            else:
                print(f"Failed: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

        print("-" * 40)
        print()
    
    print("🎉 Demo Complete!")
    print()
    print(" To use the web interface:")
    print("   1. Open: http://localhost:8000")
    print("   2. Fill in client details")
    print("   3. Get instant recommendations")
    print()
    print(" This is a demo version showing:")
    print("   • Real-time loan matching logic")
    print("   • LVR and income eligibility checks")
    print("   • Competitive rate analysis")
    print("   • Professional web interface")
    print()
    print(" The full system would:")
    print("   • Process 100+ bank documents with AI")
    print("   • Use vector database for fast retrieval")
    print("   • Provide 90%+ accuracy with Anthropic Claude")
    print("   • Complete analysis in under 3 seconds")

if __name__ == "__main__":
    test_recommendation_system()