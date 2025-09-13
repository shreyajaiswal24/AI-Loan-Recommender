#!/usr/bin/env python3
"""
Simple local server to run the AI Loan Recommender project
"""
import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Add current directory to path
sys.path.append('.')

class LoanHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        elif self.path == '/api/health':
            self.serve_health()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/recommend':
            self.serve_recommendations()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_html(self):
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>AI Loan Recommender</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 800px; margin: 0 auto;
            background: white; border-radius: 20px; padding: 40px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
        .header p { color: #666; margin: 5px 0; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input, select { 
            width: 100%; padding: 15px; border: 2px solid #e1e5e9; 
            border-radius: 10px; font-size: 16px; transition: border-color 0.3s;
        }
        input:focus, select:focus { 
            outline: none; border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 18px 40px; border: none; border-radius: 10px; 
            cursor: pointer; font-size: 18px; font-weight: 600; width: 100%; 
            transition: transform 0.2s; margin-top: 20px;
        }
        button:hover { transform: translateY(-2px); }
        .loan-card { 
            border: 2px solid #e1e5e9; border-radius: 15px; padding: 25px; 
            margin: 20px 0; background: #f8f9fa; position: relative;
            transition: transform 0.2s;
        }
        .loan-card:hover { transform: translateY(-5px); }
        .rank-badge { 
            position: absolute; top: -15px; right: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 8px 20px; border-radius: 25px; 
            font-weight: 600; font-size: 14px;
        }
        .features { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
        .feature { 
            background: #e3f2fd; color: #1976d2; padding: 6px 12px; 
            border-radius: 20px; font-size: 12px; font-weight: 500;
        }
        .loading { 
            text-align: center; padding: 60px 20px; color: #666; 
            font-size: 18px; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
        .success { 
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
            color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; 
            text-align: center; font-weight: 600;
        }
        .error { 
            background: #f44336; color: white; padding: 20px; 
            border-radius: 10px; margin: 20px 0; font-weight: 600;
        }
        .warning { 
            background: #ff9800; color: white; padding: 15px; 
            border-radius: 8px; margin: 15px 0; font-weight: 500;
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Loan Recommender</h1>
            <p>Get personalized home loan recommendations in seconds</p>
            <p><strong>Powered by AI</strong> • Running Locally</p>
        </div>
        
        <form id="loanForm">
            <div class="form-group">
                <label for="annual_income">Annual Income (AUD)</label>
                <input type="number" id="annual_income" required min="1000" placeholder="e.g., 95,000">
            </div>
            
            <div class="form-group">
                <label for="savings">Savings/Deposit (AUD)</label>
                <input type="number" id="savings" required min="0" placeholder="e.g., 85,000">
            </div>
            
            <div class="form-group">
                <label for="loan_amount">Loan Amount (AUD)</label>
                <input type="number" id="loan_amount" required min="10000" placeholder="e.g., 500,000">
            </div>
            
            <div class="form-group">
                <label for="property_value">Property Value (AUD)</label>
                <input type="number" id="property_value" required min="50000" placeholder="e.g., 580,000">
            </div>
            
            <div class="form-group">
                <label for="property_type">Property Type</label>
                <select id="property_type" required>
                    <option value="">Select property type...</option>
                    <option value="house">House</option>
                    <option value="apartment">Apartment</option>
                    <option value="townhouse">Townhouse</option>
                    <option value="investment">Investment Property</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="employment_type">Employment Type</label>
                <select id="employment_type" required>
                    <option value="">Select employment...</option>
                    <option value="full_time">Full Time</option>
                    <option value="part_time">Part Time</option>
                    <option value="casual">Casual</option>
                    <option value="self_employed">Self Employed</option>
                    <option value="contract">Contract</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="employment_length_months">Employment Length (months)</label>
                <input type="number" id="employment_length_months" required min="0" placeholder="e.g., 18">
            </div>
            
            <div class="form-group">
                <label for="credit_score">Credit Score (optional)</label>
                <input type="number" id="credit_score" min="300" max="850" placeholder="e.g., 750">
            </div>
            
            <div class="form-group">
                <label for="existing_debts">Existing Debts (AUD)</label>
                <input type="number" id="existing_debts" value="0" min="0" placeholder="e.g., 15,000">
            </div>
            
            <div class="form-group">
                <label for="dependents">Number of Dependents</label>
                <input type="number" id="dependents" value="0" min="0" placeholder="e.g., 0">
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="first_home_buyer" style="width: auto; margin-right: 10px;"> 
                    First Home Buyer
                </label>
            </div>
            
            <button type="submit">Get AI Loan Recommendations</button>
        </form>
        
        <div id="results"></div>
    </div>
    
    <script>
        document.getElementById('loanForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                annual_income: parseInt(document.getElementById('annual_income').value),
                savings: parseInt(document.getElementById('savings').value),
                loan_amount: parseInt(document.getElementById('loan_amount').value),
                property_value: parseInt(document.getElementById('property_value').value),
                property_type: document.getElementById('property_type').value,
                employment_type: document.getElementById('employment_type').value,
                employment_length_months: parseInt(document.getElementById('employment_length_months').value),
                existing_debts: parseInt(document.getElementById('existing_debts').value || 0),
                dependents: parseInt(document.getElementById('dependents').value || 0),
                first_home_buyer: document.getElementById('first_home_buyer').checked
            };
            
            const creditScore = document.getElementById('credit_score').value;
            if (creditScore) data.credit_score = parseInt(creditScore);
            
            document.getElementById('results').innerHTML = '<div class="loading">AI analyzing loan options...</div>';
            
            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                const result = await response.json();
                displayResults(result);
            } catch (error) {
                document.getElementById('results').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        });
        
        function displayResults(data) {
            let html = '<div class="success">AI Analysis Complete!</div>';
            html += '<h2 style="color: #333; text-align: center;">Top Loan Recommendations</h2>';
            html += `<p style="text-align: center; color: #666; font-size: 16px;">
                <strong>LVR:</strong> ${data.client_summary.lvr}% | 
                <strong>Deposit:</strong> ${data.client_summary.deposit}%
            </p>`;
            
            data.recommendations.forEach((rec, index) => {
                const loan = rec.loan_product;
                const rankEmoji = ['#1', '#2', '#3'][index] || '#' + (index + 1);
                
                html += `
                    <div class="loan-card">
                        <div class="rank-badge">#${index + 1}</div>
                        <h3 style="color: #333; margin-top: 0;">${rankEmoji} ${loan.bank_name}</h3>
                        <h4 style="color: #667eea; margin: 5px 0 15px 0;">${loan.product_name}</h4>
                        <p><strong>Interest Rate:</strong> ${loan.interest_rate}% | <strong>Comparison:</strong> ${loan.comparison_rate}%</p>
                        <p><strong>Monthly Payment:</strong> $${rec.estimated_monthly_payment.toLocaleString()}</p>
                        <p><strong>Application Fee:</strong> $${loan.application_fee.toLocaleString()}</p>
                        <p><strong>AI Match Score:</strong> ${rec.match_score}%</p>
                        
                        <div class="features">
                            ${loan.features.map(f => `<span class="feature">${f}</span>`).join('')}
                        </div>
                        
                        <p><strong>AI Analysis:</strong> ${rec.reasoning}</p>
                        
                        ${rec.warnings.length > 0 ? 
                            `<div class="warning"><strong>Important:</strong> ${rec.warnings.join(', ')}</div>` 
                            : ''}
                    </div>
                `;
            });
            
            html += `
                <div style="margin-top: 40px; padding: 25px; background: #f0f8ff; border-radius: 15px; text-align: center;">
                    <h3 style="color: #333;">AI-Powered Automation</h3>
                    <p style="color: #666;">This analysis replaces 3-4 hours of manual broker work with instant AI recommendations.</p>
                    <p style="color: #666; font-size: 14px;">Contact a mortgage broker to proceed with your application.</p>
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_health(self):
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
    
    def serve_recommendations(self):
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode('utf-8'))
            
            # Process recommendations using the AI logic
            result = self.get_loan_recommendations(client_data)
            
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
    
    def get_loan_recommendations(self, client_data):
        """AI Loan recommendation logic"""
        
        # Sample loan products
        LOAN_PRODUCTS = [
            {
                "id": "commbank_fhb",
                "bank_name": "Commonwealth Bank",
                "product_name": "First Home Buyer Loan",
                "interest_rate": 5.89,
                "comparison_rate": 6.18,
                "application_fee": 0,
                "max_lvr": 95.0,
                "min_income": 60000,
                "first_home_buyer_only": True,
                "features": ["No application fee", "95% LVR", "Government grants eligible"]
            },
            {
                "id": "anz_simplicity",
                "bank_name": "ANZ",
                "product_name": "Simplicity Plus",
                "interest_rate": 6.19,
                "comparison_rate": 6.20,
                "application_fee": 799,
                "max_lvr": 90.0,
                "min_income": 50000,
                "first_home_buyer_only": False,
                "features": ["Offset account", "Redraw facility", "Extra repayments"]
            },
            {
                "id": "westpac_premier",
                "bank_name": "Westpac",
                "product_name": "Premier Advantage Package",
                "interest_rate": 6.09,
                "comparison_rate": 6.18,
                "application_fee": 0,
                "max_lvr": 95.0,
                "min_income": 80000,
                "first_home_buyer_only": False,
                "features": ["No application fee", "Offset accounts", "Package benefits"]
            },
            {
                "id": "westpac_basic",
                "bank_name": "Westpac",
                "product_name": "Basic Variable",
                "interest_rate": 6.34,
                "comparison_rate": 6.36,
                "application_fee": 599,
                "max_lvr": 90.0,
                "min_income": 40000,
                "first_home_buyer_only": False,
                "features": ["Basic loan", "No ongoing fees", "Simple structure"]
            }
        ]
        
        def calculate_monthly_payment(loan_amount, annual_rate, years=30):
            monthly_rate = annual_rate / 100 / 12
            num_payments = years * 12
            
            if monthly_rate == 0:
                return loan_amount / num_payments
            
            payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            return round(payment, 2)
        
        def calculate_lvr(loan_amount, property_value):
            return (loan_amount / property_value) * 100
        
        def score_loan_match(client, loan):
            score = 100
            reasons = []
            warnings = []
            
            lvr = calculate_lvr(client["loan_amount"], client["property_value"])
            
            # LVR Check
            if lvr > loan["max_lvr"]:
                score -= 50
                warnings.append(f"LVR {lvr:.1f}% exceeds maximum {loan['max_lvr']}%")
            else:
                reasons.append(f"LVR {lvr:.1f}% within limits")
            
            # Income Check
            if client["annual_income"] < loan["min_income"]:
                score -= 30
                warnings.append(f"Income ${client['annual_income']:,} below minimum ${loan['min_income']:,}")
            else:
                reasons.append("Income requirement met")
            
            # First Home Buyer
            if client.get("first_home_buyer") and loan["first_home_buyer_only"]:
                score += 15
                reasons.append("First home buyer special rate")
            elif not client.get("first_home_buyer") and loan["first_home_buyer_only"]:
                score -= 40
                warnings.append("First home buyer only product")
            
            # Rate competitiveness
            if loan["interest_rate"] < 6.0:
                score += 10
                reasons.append("Competitive interest rate")
            elif loan["interest_rate"] > 6.3:
                score -= 5
            
            # Application fee
            if loan["application_fee"] == 0:
                score += 5
                reasons.append("No application fee")
            
            return {
                "score": max(0, min(100, score)),
                "reasons": reasons,
                "warnings": warnings
            }
        
        # Score all loans
        scored_loans = []
        
        for loan in LOAN_PRODUCTS:
            match_data = score_loan_match(client_data, loan)
            
            if match_data["score"] > 30:
                monthly_payment = calculate_monthly_payment(client_data["loan_amount"], loan["interest_rate"])
                
                scored_loans.append({
                    "loan_product": loan,
                    "match_score": match_data["score"],
                    "reasoning": "; ".join(match_data["reasons"]) if match_data["reasons"] else "Standard loan product",
                    "estimated_monthly_payment": monthly_payment,
                    "warnings": match_data["warnings"]
                })
        
        # Sort by score and take top 3
        scored_loans.sort(key=lambda x: x["match_score"], reverse=True)
        top_recommendations = scored_loans[:3]
        
        if not top_recommendations:
            raise ValueError("No suitable loan products found")
        
        lvr = calculate_lvr(client_data["loan_amount"], client_data["property_value"])
        deposit = (client_data["savings"] / client_data["property_value"]) * 100
        
        return {
            "client_summary": {
                "income": client_data["annual_income"],
                "loan_amount": client_data["loan_amount"],
                "lvr": round(lvr, 1),
                "deposit": round(deposit, 1),
                "property_type": client_data["property_type"],
                "first_home_buyer": client_data.get("first_home_buyer", False)
            },
            "recommendations": top_recommendations
        }

def main():
    print("AI Loan Recommender - Starting Local Server")
    print("=" * 55)
    print()
    
    # Change to project directory
    project_dir = '/home/shreya_24/ai_loan_recommender'
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        print(f"Changed to project directory: {project_dir}")
    else:
        print(f"Project directory not found: {project_dir}")
        print("   Continuing from current directory...")
    
    print()
    
    # Create and start server
    port = 8080
    server = HTTPServer(('localhost', port), LoanHandler)
    
    print(f"🌐 Server running at: http://localhost:{port}")
    print()
    print("📱 Open your browser and go to: http://localhost:8080")
    print()
    print("🔧 Available endpoints:")
    print(f"   GET  http://localhost:{port}/          (Main App)")
    print(f"   GET  http://localhost:{port}/api/health (Health Check)")
    print(f"   POST http://localhost:{port}/api/recommend (AI Recommendations)")
    print()
    print("🎯 Features:")
    print("   • Professional loan application form")
    print("   • Real-time AI loan matching")
    print("   • 3 ranked loan recommendations")
    print("   • LVR and payment calculations")
    print("   • Beautiful responsive design")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 55)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        print("👋 Thank you for using AI Loan Recommender!")
        server.shutdown()

if __name__ == "__main__":
    main()