#!/usr/bin/env python3
"""
Test script for the AI Loan Recommendation System
"""
import sys
import json
import requests
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_api_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_recommendation_api():
    """Test the recommendation endpoint"""
    
    # Sample client profiles for testing
    test_clients = [
        {
            "name": "First Home Buyer",
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
            "name": "High Income Family",
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
            "name": "Self-Employed Investor",
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
    
    results = []
    
    for test_client in test_clients:
        print(f"\n🧪 Testing: {test_client['name']}")
        print("-" * 30)
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/recommend",
                json=test_client["profile"],
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success in {processing_time:.2f}s")
                print(f"  Recommendations: {len(data['recommendations'])}")
                print(f"  AI Confidence: {data['ai_confidence']}")
                print(f"  Processing Time: {data['processing_time_seconds']:.2f}s")
                
                for i, rec in enumerate(data['recommendations'], 1):
                    loan = rec['loan_product']
                    print(f"  {i}. {loan['bank_name']} - {loan['product_name']}")
                    print(f"     Rate: {loan['interest_rate']}% | Score: {rec['match_score']}")
                
                results.append({
                    "client": test_client['name'],
                    "success": True,
                    "processing_time": processing_time,
                    "recommendations": len(data['recommendations']),
                    "ai_confidence": data['ai_confidence']
                })
                
            else:
                print(f"✗ Failed: HTTP {response.status_code}")
                print(f"  Error: {response.text}")
                results.append({
                    "client": test_client['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results.append({
                "client": test_client['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

def generate_test_report(results):
    """Generate test report"""
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_time = sum(r.get('processing_time', 0) for r in results if r['success']) / successful_tests
        print(f"Average Processing Time: {avg_time:.2f}s")
    
    print("\nDETAILED RESULTS:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['client']}")
        if result['success']:
            print(f"    Time: {result.get('processing_time', 0):.2f}s")
            print(f"    Recommendations: {result.get('recommendations', 0)}")
            print(f"    Confidence: {result.get('ai_confidence', 'unknown')}")
        else:
            print(f"    Error: {result.get('error', 'Unknown error')}")

def main():
    """Main test function"""
    print("🧪 AI Loan Recommendation System - Test Suite")
    print("=" * 50)
    
    # Check if server is running
    print("Checking server status...")
    if not test_api_health():
        print("✗ Server not responding at http://localhost:8000")
        print("\nTo start the server, run: python3 run.py")
        sys.exit(1)
    
    print("✓ Server is running")
    
    # Run recommendation tests
    print("\nRunning recommendation tests...")
    results = test_recommendation_api()
    
    # Generate report
    generate_test_report(results)
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    main()