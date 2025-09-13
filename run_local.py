#!/usr/bin/env python3
"""
Run a local development server that mimics Vercel's behavior
"""
import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add api directory to path
sys.path.append('./api')

class LocalServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                "status": "healthy",
                "platform": "local-dev",
                "service": "AI Loan Recommender"
            })
            self.wfile.write(response.encode())
        
        elif self.path == '/' or self.path == '/index.html':
            # Serve the main HTML file
            try:
                with open('index.html', 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        
        else:
            # Serve other static files
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/recommend':
            try:
                # Import the recommendation function
                from recommend import get_recommendations
                
                # Read the request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                client_data = json.loads(post_data.decode('utf-8'))
                
                # Get recommendations
                result = get_recommendations(client_data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps(result)
                self.wfile.write(response.encode())
                
            except Exception as e:
                # Send error response
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = json.dumps({
                    "error": str(e),
                    "message": "Internal server error"
                })
                self.wfile.write(error_response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.address_string()}] {format % args}")

def main():
    print("🚀 AI Loan Recommender - Local Development Server")
    print("=" * 55)
    print()
    
    # Change to project directory
    os.chdir('/home/shreya_24/ai_loan_recommender')
    
    # Check if key files exist
    if not os.path.exists('index.html'):
        print("❌ index.html not found!")
        return
    
    if not os.path.exists('api/recommend.py'):
        print("❌ api/recommend.py not found!")
        return
    
    print("✅ All required files found")
    print()
    
    # Create and start server
    port = 8080
    server = HTTPServer(('localhost', port), LocalServerHandler)
    
    print(f"🌐 Server starting on http://localhost:{port}")
    print()
    print("📱 Open in your browser: http://localhost:8080")
    print()
    print("🔧 Available endpoints:")
    print(f"   GET  http://localhost:{port}/")
    print(f"   GET  http://localhost:{port}/api/health")
    print(f"   POST http://localhost:{port}/api/recommend")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 55)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        print("👋 Goodbye!")
        server.shutdown()

if __name__ == "__main__":
    main()