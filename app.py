#!/usr/bin/env python3
"""
Vercel-optimized AI Loan Recommendation System
Lightweight version for cloud deployment
"""
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum

# Vercel Handler
app = FastAPI(
    title="AI Loan Recommender",
    version="1.0.0",
    description="AI-powered loan recommendation system for Vercel deployment"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    INVESTMENT = "investment"

class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time" 
    CASUAL = "casual"
    SELF_EMPLOYED = "self_employed"
    CONTRACT = "contract"

class ClientProfile(BaseModel):
    annual_income: int = Field(..., description="Annual gross income in AUD", ge=1000)
    savings: int = Field(..., description="Total savings/deposit in AUD", ge=0)
    loan_amount: int = Field(..., description="Requested loan amount in AUD", ge=10000)
    property_value: int = Field(..., description="Property value in AUD", ge=50000)
    property_type: PropertyType = Field(..., description="Type of property")
    employment_type: EmploymentType = Field(..., description="Employment status")
    employment_length_months: int = Field(..., description="Length of current employment in months", ge=0)
    credit_score: Optional[int] = Field(None, description="Credit score (300-850)", ge=300, le=850)
    existing_debts: int = Field(0, description="Total existing debts in AUD", ge=0)
    dependents: int = Field(0, description="Number of dependents", ge=0)
    first_home_buyer: bool = Field(False, description="Is this their first home purchase?")
    
    @validator('property_value')
    def property_value_must_exceed_loan(cls, v, values):
        if 'loan_amount' in values and v < values['loan_amount']:
            raise ValueError('Property value must be greater than loan amount')
        return v
    
    @property
    def loan_to_value_ratio(self) -> float:
        return (self.loan_amount / self.property_value) * 100
    
    @property
    def deposit_percentage(self) -> float:
        return (self.savings / self.property_value) * 100

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

def calculate_monthly_payment(loan_amount: int, annual_rate: float, years: int = 30) -> float:
    """Calculate estimated monthly payment"""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(payment, 2)

def score_loan_match(client: ClientProfile, loan: dict) -> dict:
    """AI loan matching logic"""
    score = 100
    reasons = []
    warnings = []
    
    # LVR Check
    if client.loan_to_value_ratio > loan["max_lvr"]:
        score -= 50
        warnings.append(f"LVR {client.loan_to_value_ratio:.1f}% exceeds maximum {loan['max_lvr']}%")
    else:
        reasons.append(f"LVR {client.loan_to_value_ratio:.1f}% within limits")
    
    # Income Check
    if client.annual_income < loan["min_income"]:
        score -= 30
        warnings.append(f"Income ${client.annual_income:,} below minimum ${loan['min_income']:,}")
    else:
        reasons.append("Income requirement met")
    
    # First Home Buyer
    if client.first_home_buyer and loan["first_home_buyer_only"]:
        score += 15
        reasons.append("First home buyer special rate")
    elif not client.first_home_buyer and loan["first_home_buyer_only"]:
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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Loan Recommender</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                max-width: 800px; margin: 0 auto; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                background: white; border-radius: 20px; padding: 40px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #333; margin: 0; font-size: 2.5em; }
            .header p { color: #666; margin: 10px 0; }
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
                <h1>🤖 AI Loan Recommender</h1>
                <p>Get personalized home loan recommendations in seconds</p>
                <p><strong>Powered by AI</strong> • Replacing manual broker work</p>
            </div>
            
            <form id="loanForm">
                <div class="form-group">
                    <label for="annual_income">💰 Annual Income (AUD)</label>
                    <input type="number" id="annual_income" required min="1000" placeholder="e.g., 95,000">
                </div>
                
                <div class="form-group">
                    <label for="savings">🏦 Savings/Deposit (AUD)</label>
                    <input type="number" id="savings" required min="0" placeholder="e.g., 85,000">
                </div>
                
                <div class="form-group">
                    <label for="loan_amount">📊 Loan Amount (AUD)</label>
                    <input type="number" id="loan_amount" required min="10000" placeholder="e.g., 500,000">
                </div>
                
                <div class="form-group">
                    <label for="property_value">🏠 Property Value (AUD)</label>
                    <input type="number" id="property_value" required min="50000" placeholder="e.g., 580,000">
                </div>
                
                <div class="form-group">
                    <label for="property_type">🏘️ Property Type</label>
                    <select id="property_type" required>
                        <option value="">Select property type...</option>
                        <option value="house">House</option>
                        <option value="apartment">Apartment</option>
                        <option value="townhouse">Townhouse</option>
                        <option value="investment">Investment Property</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="employment_type">💼 Employment Type</label>
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
                    <label for="employment_length_months">📅 Employment Length (months)</label>
                    <input type="number" id="employment_length_months" required min="0" placeholder="e.g., 18">
                </div>
                
                <div class="form-group">
                    <label for="credit_score">📈 Credit Score (optional)</label>
                    <input type="number" id="credit_score" min="300" max="850" placeholder="e.g., 750">
                </div>
                
                <div class="form-group">
                    <label for="existing_debts">💳 Existing Debts (AUD)</label>
                    <input type="number" id="existing_debts" value="0" min="0" placeholder="e.g., 15,000">
                </div>
                
                <div class="form-group">
                    <label for="dependents">👨‍👩‍👧‍👦 Number of Dependents</label>
                    <input type="number" id="dependents" value="0" min="0" placeholder="e.g., 0">
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="first_home_buyer" style="width: auto; margin-right: 10px;"> 
                        🏡 First Home Buyer
                    </label>
                </div>
                
                <button type="submit">🚀 Get AI Loan Recommendations</button>
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
                
                document.getElementById('results').innerHTML = '<div class="loading">🔍 AI analyzing loan options...</div>';
                
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
                        `<div class="error">❌ Error: ${error.message}</div>`;
                }
            });
            
            function displayResults(data) {
                let html = '<div class="success">✅ AI Analysis Complete!</div>';
                html += '<h2 style="color: #333; text-align: center;">🏆 Top Loan Recommendations</h2>';
                html += `<p style="text-align: center; color: #666; font-size: 16px;">
                    <strong>LVR:</strong> ${data.client_summary.lvr}% | 
                    <strong>Deposit:</strong> ${data.client_summary.deposit}%
                </p>`;
                
                data.recommendations.forEach((rec, index) => {
                    const loan = rec.loan_product;
                    const rankEmoji = ['🥇', '🥈', '🥉'][index] || '🏅';
                    
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
                                `<div class="warning"><strong>⚠️ Important:</strong> ${rec.warnings.join(', ')}</div>` 
                                : ''}
                        </div>
                    `;
                });
                
                html += `
                    <div style="margin-top: 40px; padding: 25px; background: #f0f8ff; border-radius: 15px; text-align: center;">
                        <h3 style="color: #333;">🤖 AI-Powered Automation</h3>
                        <p style="color: #666;">This analysis replaces 3-4 hours of manual broker work with instant AI recommendations.</p>
                        <p style="color: #666; font-size: 14px;">Contact a mortgage broker to proceed with your application.</p>
                    </div>
                `;
                
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/recommend")
async def get_recommendations(client_profile: ClientProfile):
    """AI loan recommendations API"""
    try:
        scored_loans = []
        
        for loan in LOAN_PRODUCTS:
            match_data = score_loan_match(client_profile, loan)
            
            if match_data["score"] > 30:
                monthly_payment = calculate_monthly_payment(client_profile.loan_amount, loan["interest_rate"])
                
                scored_loans.append({
                    "loan_product": loan,
                    "match_score": match_data["score"],
                    "reasoning": "; ".join(match_data["reasons"]) if match_data["reasons"] else "Standard loan product",
                    "estimated_monthly_payment": monthly_payment,
                    "warnings": match_data["warnings"]
                })
        
        scored_loans.sort(key=lambda x: x["match_score"], reverse=True)
        top_recommendations = scored_loans[:3]
        
        if not top_recommendations:
            raise HTTPException(status_code=404, detail="No suitable loan products found")
        
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "healthy", "platform": "vercel"}

# Vercel handler
def handler(request):
    return app(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)