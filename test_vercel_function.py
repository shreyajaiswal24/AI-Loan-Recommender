#!/usr/bin/env python3
"""
Test the Vercel function locally
"""
import sys
sys.path.append('./api')

from index import handler, get_recommendations
import json

def test_vercel_function():
    print("🧪 Testing Vercel Function Locally")
    print("=" * 40)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    health_request = {
        'httpMethod': 'GET',
        'path': '/api/health',
        'body': ''
    }
    
    try:
        response = handler(health_request)
        print(f"✅ Health check: {response['statusCode']}")
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"   Response: {body}")
        else:
            print(f"   Error: {response}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print()
    
    # Test 2: Loan recommendations
    print("2. Testing loan recommendations...")
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
    
    recommend_request = {
        'httpMethod': 'POST',
        'path': '/api/recommend',
        'body': json.dumps(test_data)
    }
    
    try:
        response = handler(recommend_request)
        print(f"✅ Recommendations: {response['statusCode']}")
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"   Found {len(body['recommendations'])} recommendations")
            for i, rec in enumerate(body['recommendations'], 1):
                loan = rec['loan_product']
                print(f"   {i}. {loan['bank_name']} - {loan['interest_rate']}% - Score: {rec['match_score']}")
        else:
            print(f"   Error: {response}")
    except Exception as e:
        print(f"❌ Recommendations failed: {e}")
    
    print()
    
    # Test 3: HTML page
    print("3. Testing HTML page...")
    html_request = {
        'httpMethod': 'GET',
        'path': '/',
        'body': ''
    }
    
    try:
        response = handler(html_request)
        print(f"✅ HTML page: {response['statusCode']}")
        if response['statusCode'] == 200:
            html_length = len(response['body'])
            print(f"   HTML length: {html_length} characters")
            print(f"   Contains form: {'<form' in response['body']}")
        else:
            print(f"   Error: {response}")
    except Exception as e:
        print(f"❌ HTML page failed: {e}")
    
    print()
    print("🎉 Local testing complete!")
    print("If all tests passed, the Vercel function should work!")

if __name__ == "__main__":
    test_vercel_function()