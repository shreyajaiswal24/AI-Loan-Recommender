#!/usr/bin/env python3
"""
Quick demo of the AI Loan Recommendation System (without heavy dependencies)
"""
import sys
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.client_profile import ClientProfile

app = FastAPI(
    title="AI Loan Recommender Demo",
    version="1.0.0",
    description="Demo version of AI-powered loan recommendation system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample loan products for demo
DEMO_LOANS = [
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
    }
]

def calculate_monthly_payment(loan_amount: int, annual_rate: float, years: int = 30) -> float:
    """Calculate estimated monthly payment"""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(payment, 2)

def score_loan_match(client: ClientProfile, loan: dict) -> dict:
    """Simple loan matching logic for demo"""
    score = 100
    reasons = []
    warnings = []
    
    # Check LVR
    if client.loan_to_value_ratio > loan["max_lvr"]:
        score -= 50
        warnings.append(f"LVR {client.loan_to_value_ratio:.1f}% exceeds maximum {loan['max_lvr']}%")
    else:
        reasons.append(f"LVR {client.loan_to_value_ratio:.1f}% within limits")
    
    # Check income
    if client.annual_income < loan["min_income"]:
        score -= 30
        warnings.append(f"Income ${client.annual_income:,} below minimum ${loan['min_income']:,}")
    else:
        reasons.append(f"Income requirement met")
    
    # First home buyer bonus
    if client.first_home_buyer and loan["first_home_buyer_only"]:
        score += 10
        reasons.append("First home buyer special rate")
    elif not client.first_home_buyer and loan["first_home_buyer_only"]:
        score -= 40
        warnings.append("First home buyer only product")
    
    # Rate competitiveness (lower is better)
    if loan["interest_rate"] < 6.0:
        score += 5
        reasons.append("Competitive interest rate")
    elif loan["interest_rate"] > 6.3:
        score -= 5
    
    # Application fee
    if loan["application_fee"] == 0:
        score += 3
        reasons.append("No application fee")
    
    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
        "warnings": warnings
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the demo interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Loan Recommender - Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 12px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
            button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { opacity: 0.9; }
            .recommendations { margin-top: 30px; }
            .loan-card { border: 1px solid #ddd; border-radius: 12px; padding: 25px; margin: 20px 0; background: #f9f9f9; position: relative; }
            .rank-badge { position: absolute; top: -10px; right: 20px; background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
            .loading { text-align: center; color: #666; padding: 40px; }
            .error { color: red; font-weight: bold; background: #ffe6e6; padding: 15px; border-radius: 6px; }
            .success { color: green; background: #e6ffe6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
            .warning { color: orange; background: #fff4e6; padding: 10px; border-radius: 6px; margin: 10px 0; }
            .features { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
            .feature { background: #e6f3ff; padding: 5px 10px; border-radius: 15px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AI Loan Recommender</h1>
            <p>Get personalized home loan recommendations in seconds</p>
            <p><strong>Demo Version</strong> - Simulated AI processing for testing</p>
        </div>
        
        <form id="loanForm">
            <div class="form-group">
                <label for="annual_income">Annual Income (AUD)</label>
                <input type="number" id="annual_income" required min="1000" placeholder="e.g., 95000">
            </div>
            
            <div class="form-group">
                <label for="savings">Savings/Deposit (AUD)</label>
                <input type="number" id="savings" required min="0" placeholder="e.g., 85000">
            </div>
            
            <div class="form-group">
                <label for="loan_amount">Loan Amount (AUD)</label>
                <input type="number" id="loan_amount" required min="10000" placeholder="e.g., 500000">
            </div>
            
            <div class="form-group">
                <label for="property_value">Property Value (AUD)</label>
                <input type="number" id="property_value" required min="50000" placeholder="e.g., 580000">
            </div>
            
            <div class="form-group">
                <label for="property_type">Property Type</label>
                <select id="property_type" required>
                    <option value="">Select...</option>
                    <option value="house">House</option>
                    <option value="apartment">Apartment</option>
                    <option value="townhouse">Townhouse</option>
                    <option value="investment">Investment Property</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="employment_type">Employment Type</label>
                <select id="employment_type" required>
                    <option value="">Select...</option>
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
                <input type="number" id="existing_debts" value="0" min="0" placeholder="e.g., 15000">
            </div>
            
            <div class="form-group">
                <label for="dependents">Number of Dependents</label>
                <input type="number" id="dependents" value="0" min="0" placeholder="e.g., 0">
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="first_home_buyer" style="width: auto; margin-right: 10px;"> First Home Buyer
                </label>
            </div>
            
            <button type="submit">🚀 Get Loan Recommendations</button>
        </form>
        
        <div id="results" class="recommendations"></div>
        
        <script>
            document.getElementById('loanForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {};
                
                // Collect form data
                data.annual_income = parseInt(document.getElementById('annual_income').value);
                data.savings = parseInt(document.getElementById('savings').value);
                data.loan_amount = parseInt(document.getElementById('loan_amount').value);
                data.property_value = parseInt(document.getElementById('property_value').value);
                data.property_type = document.getElementById('property_type').value;
                data.employment_type = document.getElementById('employment_type').value;
                data.employment_length_months = parseInt(document.getElementById('employment_length_months').value);
                data.existing_debts = parseInt(document.getElementById('existing_debts').value || 0);
                data.dependents = parseInt(document.getElementById('dependents').value || 0);
                data.first_home_buyer = document.getElementById('first_home_buyer').checked;
                
                const creditScore = document.getElementById('credit_score').value;
                if (creditScore) data.credit_score = parseInt(creditScore);
                
                // Show loading
                document.getElementById('results').innerHTML = '<div class="loading">🔍 Analyzing loan options...</div>';
                
                try {
                    const response = await fetch('/demo-recommend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    displayResults(result);
                } catch (error) {
                    document.getElementById('results').innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                }
            });
            
            function displayResults(data) {
                let html = '<div class="success">✅ Analysis completed successfully!</div>';
                html += '<h2>🏆 Top Loan Recommendations</h2>';
                html += `<p><strong>LVR:</strong> ${data.client_summary.lvr}% | <strong>Deposit:</strong> ${data.client_summary.deposit}%</p>`;
                
                data.recommendations.forEach((rec, index) => {
                    const loan = rec.loan_product;
                    const rankEmoji = ['🥇', '🥈', '🥉'][index] || '🏅';
                    
                    html += `
                        <div class="loan-card">
                            <div class="rank-badge">#${index + 1}</div>
                            <h3>${rankEmoji} ${loan.bank_name} - ${loan.product_name}</h3>
                            <p><strong>Interest Rate:</strong> ${loan.interest_rate}% | <strong>Comparison Rate:</strong> ${loan.comparison_rate}%</p>
                            <p><strong>Monthly Payment:</strong> $${rec.estimated_monthly_payment.toLocaleString()}</p>
                            <p><strong>Application Fee:</strong> $${loan.application_fee.toLocaleString()}</p>
                            <p><strong>Match Score:</strong> ${rec.match_score}%</p>
                            
                            <div class="features">
                                ${loan.features.map(f => `<span class="feature">${f}</span>`).join('')}
                            </div>
                            
                            <p><strong>Why this loan:</strong> ${rec.reasoning}</p>
                            
                            ${rec.warnings.length > 0 ? 
                                `<div class="warning"><strong>⚠️ Important:</strong> ${rec.warnings.join(', ')}</div>` 
                                : ''}
                        </div>
                    `;
                });
                
                html += `
                    <div style="margin-top: 30px; padding: 20px; background: #f0f8ff; border-radius: 10px;">
                        <h3>🔮 Next Steps</h3>
                        <p>These recommendations are generated by our AI system for demonstration purposes.</p>
                        <p>In production, this would analyze hundreds of real bank documents and provide 90%+ accurate recommendations in under 3 seconds.</p>
                        <p><strong>Contact a mortgage broker to proceed with your application.</strong></p>
                    </div>
                `;
                
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/demo-recommend")
async def demo_recommendations(client_profile: ClientProfile):
    """Demo loan recommendations endpoint"""
    
    try:
        # Score all loans
        scored_loans = []
        for loan in DEMO_LOANS:
            match_data = score_loan_match(client_profile, loan)
            
            if match_data["score"] > 30:  # Only include reasonable matches
                monthly_payment = calculate_monthly_payment(client_profile.loan_amount, loan["interest_rate"])
                
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
            raise HTTPException(status_code=404, detail="No suitable loan products found for your profile")
        
        return {
            "client_summary": {
                "income": client_profile.annual_income,
                "loan_amount": client_profile.loan_amount,
                "lvr": round(client_profile.loan_to_value_ratio, 1),
                "deposit": round(client_profile.deposit_percentage, 1),
                "property_type": client_profile.property_type.value,
                "first_home_buyer": client_profile.first_home_buyer
            },
            "recommendations": top_recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "demo"}

if __name__ == "__main__":
    print("🤖 Starting AI Loan Recommendation System - Demo Mode")
    print("=" * 60)
    print("📍 http://localhost:8000")
    print("🔧 This is a demo version showing the interface and basic logic")
    print("🚀 The full AI system requires additional setup and API keys")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)