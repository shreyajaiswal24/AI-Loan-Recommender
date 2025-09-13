#!/usr/bin/env python3
"""
Test the new local setup with static HTML + API endpoints
"""
import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
import requests

# Add api directory to path
sys.path.append('./api')

def test_api_endpoints():
    """Test individual API endpoints"""
    print("🧪 Testing API Endpoints Individually")
    print("=" * 40)
    
    # Test recommend endpoint
    try:
        from api.recommend import handler as recommend_handler, get_recommendations
        
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
        print("✅ Recommend function works")
        print(f"   Found {len(result['recommendations'])} recommendations")
        for i, rec in enumerate(result['recommendations'], 1):
            loan = rec['loan_product']
            print(f"   {i}. {loan['bank_name']} - {loan['interest_rate']}% - Score: {rec['match_score']}")
        
    except Exception as e:
        print(f"❌ Recommend function failed: {e}")
    
    print()
    
    # Test health endpoint
    try:
        from api.health import handler as health_handler
        print("✅ Health function loads successfully")
    except Exception as e:
        print(f"❌ Health function failed: {e}")

def run_simple_server():
    """Run a simple HTTP server to test the setup"""
    print("🌐 Starting Local Test Server")
    print("=" * 40)
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/api/recommend':
                try:
                    # Import and use the recommend handler
                    sys.path.append('./api')
                    from recommend import get_recommendations
                    
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    client_data = json.loads(post_data.decode('utf-8'))
                    
                    result = get_recommendations(client_data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = json.dumps(result)
                    self.wfile.write(response.encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    error_response = json.dumps({"error": str(e)})
                    self.wfile.write(error_response.encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_GET(self):
            if self.path == '/api/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps({
                    "status": "healthy",
                    "platform": "local",
                    "service": "AI Loan Recommender"
                })
                self.wfile.write(response.encode())
            else:
                # Serve static files
                super().do_GET()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
    
    # Change to project directory
    os.chdir('/home/shreya_24/ai_loan_recommender')
    
    # Start server
    server = HTTPServer(('localhost', 8080), CustomHandler)
    
    print("🚀 Server starting at http://localhost:8080")
    print("📱 Open http://localhost:8080 in your browser")
    print("🔧 API endpoints:")
    print("   GET  /api/health")
    print("   POST /api/recommend")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

def test_with_requests():
    """Test the server with requests"""
    print("🔄 Testing Server with HTTP Requests")
    print("=" * 40)
    
    # Give server time to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    print()
    
    # Test recommend endpoint
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
    
    try:
        response = requests.post(
            "http://localhost:8080/api/recommend",
            json=test_data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommend endpoint working")
            print(f"   Found {len(result['recommendations'])} recommendations")
            for i, rec in enumerate(result['recommendations'], 1):
                loan = rec['loan_product']
                print(f"   {i}. {loan['bank_name']} - {loan['interest_rate']}%")
        else:
            print(f"❌ Recommend endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Recommend endpoint error: {e}")

def main():
    print("🧪 AI Loan Recommender - Local Testing")
    print("=" * 50)
    print()
    
    # Test 1: API functions directly
    test_api_endpoints()
    print()
    
    # Test 2: Check if HTML file exists
    if os.path.exists('index.html'):
        print("✅ index.html exists")
        with open('index.html', 'r') as f:
            content = f.read()
            print(f"   HTML size: {len(content)} characters")
            print(f"   Contains form: {'<form' in content}")
    else:
        print("❌ index.html missing")
    
    print()
    
    # Test 3: Start server in background and test
    print("Starting integrated test server...")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_simple_server, daemon=True)
    server_thread.start()
    
    # Test the server
    test_with_requests()
    
    print()
    print("🎉 Local testing complete!")
    print()
    print("📱 To test the web interface:")
    print("   1. Open http://localhost:8080 in your browser")
    print("   2. Fill out the loan form")
    print("   3. Click 'Get AI Loan Recommendations'")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()