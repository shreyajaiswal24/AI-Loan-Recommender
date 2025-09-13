#!/usr/bin/env python3
"""
Test the fixed AI Loan Recommendation System
"""
import requests
import json

def test_fixed_system():
    print("🛠️  Testing FIXED AI Loan Recommendation System")
    print("=" * 60)
    print("🌐 Server: http://localhost:8001")
    print("🔧 Fixed validation and form handling")
    print()
    
    # Test data
    test_data = {
        "annual_income": 95000,
        "savings": 85000,
        "loan_amount": 500000,
        "property_value": 580000,
        "property_type": "apartment",
        "employment_type": "full_time",
        "employment_length_months": 18,
        "existing_debts": 15000,
        "dependents": 0,
        "first_home_buyer": True
    }
    
    print("📊 Test Data:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        print("🚀 Making API request...")
        response = requests.post(
            "http://localhost:8001/demo-recommend",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! API is working correctly")
            print()
            print("📈 Results:")
            print(f"   LVR: {data['client_summary']['lvr']}%")
            print(f"   Deposit: {data['client_summary']['deposit']}%")
            print(f"   Recommendations: {len(data['recommendations'])}")
            print()
            
            for i, rec in enumerate(data['recommendations'], 1):
                loan = rec['loan_product']
                print(f"🏆 #{i} - {loan['bank_name']} {loan['product_name']}")
                print(f"    Rate: {loan['interest_rate']}% | Monthly: ${rec['estimated_monthly_payment']:,.2f}")
                print(f"    Score: {rec['match_score']}%")
                print()
            
            print("🎉 The 422 error is now FIXED!")
            print("📱 You can now use the web interface at: http://localhost:8001")
            
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_fixed_system()