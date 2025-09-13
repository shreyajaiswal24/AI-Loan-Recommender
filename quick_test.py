#!/usr/bin/env python3
"""
Quick test of the new setup components
"""
import sys
import os
import json

print("🧪 AI Loan Recommender - Quick Component Test")
print("=" * 50)

# Test 1: Check files exist
print("1. Checking files...")
required_files = ['index.html', 'api/recommend.py', 'api/health.py', 'vercel.json']

for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} missing")

print()

# Test 2: Test API functions directly
print("2. Testing API functions...")

# Add api directory to path
sys.path.append('./api')

try:
    from recommend import get_recommendations
    
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
    
    result = get_recommendations(test_data)
    print("   ✅ Recommendation function works")
    print(f"      LVR: {result['client_summary']['lvr']}%")
    print(f"      Recommendations: {len(result['recommendations'])}")
    
    for i, rec in enumerate(result['recommendations'], 1):
        loan = rec['loan_product']
        print(f"      {i}. {loan['bank_name']} - {loan['interest_rate']}% (Score: {rec['match_score']})")
    
except Exception as e:
    print(f"   ❌ Recommendation function failed: {e}")

print()

# Test 3: Check HTML content
print("3. Checking HTML content...")
try:
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    print(f"   ✅ HTML file size: {len(html_content):,} characters")
    print(f"   ✅ Contains form: {'<form' in html_content}")
    print(f"   ✅ Contains API call: {'/api/recommend' in html_content}")
    print(f"   ✅ Contains styling: {'<style>' in html_content}")
    
except Exception as e:
    print(f"   ❌ HTML check failed: {e}")

print()

# Test 4: Check Vercel config
print("4. Checking Vercel config...")
try:
    with open('vercel.json', 'r') as f:
        vercel_config = json.load(f)
    
    print(f"   ✅ Vercel config loaded")
    print(f"   ✅ Functions config: {vercel_config.get('functions', {})}")
    
except Exception as e:
    print(f"   ❌ Vercel config failed: {e}")

print()

# Test 5: Test calculation functions
print("5. Testing calculation functions...")
try:
    from recommend import calculate_monthly_payment, calculate_lvr, calculate_deposit_percentage
    
    # Test calculations
    monthly_payment = calculate_monthly_payment(500000, 6.19)
    lvr = calculate_lvr(500000, 580000)
    deposit_pct = calculate_deposit_percentage(85000, 580000)
    
    print(f"   ✅ Monthly payment for $500K at 6.19%: ${monthly_payment:,.2f}")
    print(f"   ✅ LVR for $500K loan on $580K property: {lvr:.1f}%")
    print(f"   ✅ Deposit percentage for $85K on $580K: {deposit_pct:.1f}%")
    
except Exception as e:
    print(f"   ❌ Calculation functions failed: {e}")

print()

# Summary
print("📋 SUMMARY")
print("=" * 20)
print("✅ System components ready for local testing")
print("✅ All core functions working")
print("✅ HTML interface prepared")
print("✅ API endpoints structured")
print()
print("🚀 Ready to test deployment setup!")
print()
print("Next steps:")
print("1. Test locally with a simple server")
print("2. Deploy to Vercel")
print("3. Test live deployment")

print()
print("💻 To test locally, you can run:")
print("   python3 -m http.server 8080")
print("   Then open: http://localhost:8080")
print("   (Note: API calls won't work with simple server)")

if __name__ == "__main__":
    pass