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
        elif self.path == '/api/comprehensive-check':
            self.serve_comprehensive_check()
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
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
        .analysis-header {
            padding: 25px; border-radius: 15px; text-align: center; margin: 30px 0;
        }
        .analysis-header.approved { background: #4caf50; color: white; }
        .analysis-header.conditional { background: #ff9800; color: white; }
        .analysis-header.declined { background: #f44336; color: white; }
        .analysis-header.refer_specialist { background: #2196f3; color: white; }
        .metrics-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            padding: 20px; border-radius: 10px; text-align: center;
            border: 1px solid #e1e5e9; transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-2px); }
        .lender-section { margin: 30px 0; }
        .lender-section h3 { margin-bottom: 15px; font-size: 1.2em; }
        .lender-badges { display: flex; flex-wrap: wrap; gap: 10px; }
        .lender-badge { padding: 8px 15px; border-radius: 20px; font-weight: 500; }
        .lender-badge.approved { background: #e8f5e8; color: #2e7d2e; }
        .lender-badge.conditional { background: #fff3e0; color: #f57c00; }
        .lender-badge.declined { background: #ffebee; color: #c62828; }
        .analysis-section { margin: 30px 0; }
        .analysis-section h3 { margin-bottom: 15px; font-size: 1.2em; }
        .analysis-list div {
            background: #f8f9fa; padding: 12px; margin: 8px 0; 
            border-left: 4px solid #667eea; border-radius: 5px;
        }
        .analysis-list.conditions div { border-left-color: #ff9800; background: #fff3e0; }
        .analysis-list.recommendations div { border-left-color: #2196f3; background: #e3f2fd; }
        .form-section { margin: 30px 0; }
        .form-section h2 {
            color: #333; margin-bottom: 25px; display: flex; align-items: center;
            font-size: 1.5em; border-bottom: 2px solid #e1e5e9; padding-bottom: 10px;
        }
        .form-section-icon {
            background: #667eea; color: white; padding: 8px; border-radius: 8px; 
            margin-right: 15px; width: 40px; height: 40px; display: flex; 
            align-items: center; justify-content: center; font-weight: bold;
            transition: all 0.3s ease;
        }
        .form-section:hover .form-section-icon {
            background: #5a6fd8; transform: scale(1.05);
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .form-group-inline { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .checkbox-group { 
            display: flex; align-items: center; justify-content: flex-start;
            padding: 10px 15px; border-radius: 8px; 
            transition: all 0.3s ease; cursor: pointer; border: 1px solid #e1e5e9;
            background: #fafafa; width: 100%;
        }
        .checkbox-group:hover { 
            background: #f0f4ff; border-color: #c3d4ff; transform: translateX(3px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .checkbox-group input { 
            margin-right: 12px; cursor: pointer; flex-shrink: 0;
            width: 16px; height: 16px;
        }
        .checkbox-group input:checked + label { color: #667eea; font-weight: 600; }
        .checkbox-group label { 
            cursor: pointer; font-weight: 500; color: #555; font-size: 0.9em;
            text-align: left; flex: 1; margin: 0;
        }
        input:hover, select:hover { border-color: #667eea; transform: translateY(-1px); }
        button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .header h1 { font-size: 2em; }
            .form-row { grid-template-columns: 1fr; gap: 15px; }
            .form-section-icon { width: 35px; height: 35px; font-size: 0.9em; }
            .form-section h2 { font-size: 1.3em; }
            .checkbox-group { padding: 8px 12px; }
            .checkbox-group input { margin-right: 10px; width: 14px; height: 14px; }
            .checkbox-group label { font-size: 0.85em; }
            .metrics-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Loan Recommender</h1>
            <p>Get personalized home loan recommendations in seconds</p>
            <p><strong>Powered by AI</strong> - Running Locally</p>
        </div>
        
        <form id="loanForm">
            <!-- Personal & Financial Details Section -->
            <div class="form-section">
                <h2>
                    <span class="form-section-icon">P</span>
                    Personal & Financial Details
                </h2>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="annual_income">Annual Income (AUD) *</label>
                        <input type="number" id="annual_income" required min="30000" placeholder="e.g., 95,000">
                    </div>
                    <div class="form-group">
                        <label for="employment_type">Employment Type *</label>
                        <select id="employment_type" required>
                            <option value="">Select employment...</option>
                            <option value="permanent">Permanent Full Time</option>
                            <option value="casual">Casual</option>
                            <option value="self_employed">Self Employed</option>
                            <option value="contract">Contract</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="employment_months">Employment Length (months) *</label>
                        <input type="number" id="employment_months" required min="0" placeholder="e.g., 18">
                    </div>
                    <div class="form-group">
                        <label for="credit_score">Credit Score *</label>
                        <input type="number" id="credit_score" required min="300" max="850" placeholder="e.g., 750" value="700">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="monthly_expenses">Monthly Living Expenses (AUD) *</label>
                        <input type="number" id="monthly_expenses" required min="1000" placeholder="e.g., 3,500">
                    </div>
                    <div class="form-group">
                        <label for="existing_monthly_debts">Existing Monthly Debts (AUD)</label>
                        <input type="number" id="existing_monthly_debts" value="0" min="0" placeholder="e.g., 800">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dependents">Number of Dependents</label>
                        <input type="number" id="dependents" value="0" min="0" max="10" placeholder="0">
                    </div>
                    <div class="form-group">
                        <label style="margin-bottom: 15px; font-weight: 600; color: #333;">Application Type</label>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                            <div class="checkbox-group">
                                <input type="checkbox" id="is_couple">
                                <label for="is_couple">Joint Application (Couple)</label>
                            </div>
                            <div class="checkbox-group">
                                <input type="checkbox" id="first_home_buyer">
                                <label for="first_home_buyer">First Home Buyer</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loan & Property Details Section -->
            <div class="form-section">
                <h2>
                    <span class="form-section-icon">L</span>
                    Loan & Property Details
                </h2>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="requested_loan_amount">Requested Loan Amount (AUD) *</label>
                        <input type="number" id="requested_loan_amount" required min="10000" placeholder="e.g., 500,000">
                    </div>
                    <div class="form-group">
                        <label for="property_value">Property Value (AUD) *</label>
                        <input type="number" id="property_value" required min="50000" placeholder="e.g., 650,000">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="deposit_amount">Deposit Amount (AUD) *</label>
                        <input type="number" id="deposit_amount" required min="0" placeholder="e.g., 130,000">
                    </div>
                    <div class="form-group">
                        <label for="loan_term_years">Loan Term (years) *</label>
                        <select id="loan_term_years" required>
                            <option value="30" selected>30 years</option>
                            <option value="25">25 years</option>
                            <option value="20">20 years</option>
                            <option value="15">15 years</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="property_type">Property Type *</label>
                        <select id="property_type" required onchange="toggleLandSize()">
                            <option value="">Select property type...</option>
                            <option value="house">House</option>
                            <option value="unit">Unit</option>
                            <option value="apartment">Apartment</option>
                            <option value="townhouse">Townhouse</option>
                            <option value="villa">Villa</option>
                            <option value="studio_apartment">Studio Apartment</option>
                            <option value="rural_residential">Rural Residential</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="living_area_sqm">Living Area (Square Meters) *</label>
                        <input type="number" id="living_area_sqm" required min="20" placeholder="e.g., 120">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="postcode">Property Postcode *</label>
                        <input type="text" id="postcode" required pattern="[0-9]{4}" placeholder="e.g., 3141" maxlength="4">
                    </div>
                    <div class="form-group" id="land_size_group">
                        <label for="land_size_hectares">Land Size (Hectares)</label>
                        <input type="number" id="land_size_hectares" step="0.01" min="0" placeholder="e.g., 0.5" value="0">
                    </div>
                </div>
            </div>

            <!-- Additional Details Section -->
            <div class="form-section">
                <h2>
                    <span class="form-section-icon">A</span>
                    Additional Details
                </h2>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="deposit_source">Deposit Source *</label>
                        <select id="deposit_source" required>
                            <option value="genuine_savings">Genuine Savings</option>
                            <option value="gift">Gift from Family</option>
                            <option value="equity">Property Equity</option>
                            <option value="inheritance">Inheritance</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="previous_defaults">Previous Credit Defaults *</label>
                        <select id="previous_defaults" required>
                            <option value="0">None</option>
                            <option value="1">1 Default</option>
                            <option value="2">2 Defaults</option>
                            <option value="3">3+ Defaults</option>
                        </select>
                    </div>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <label style="margin-bottom: 20px; font-weight: 600; color: #333; display: block; font-size: 1.1em;">Additional Risk Factors</label>
                    <div class="form-row">
                        <div class="form-group">
                            <label style="margin-bottom: 12px; font-weight: 600; color: #555; font-size: 0.95em;">Financial History</label>
                            <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                                <div class="checkbox-group">
                                    <input type="checkbox" id="bankruptcy_history">
                                    <label for="bankruptcy_history">Previous Bankruptcy</label>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label style="margin-bottom: 12px; font-weight: 600; color: #555; font-size: 0.95em;">Property Risks</label>
                            <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                                <div class="checkbox-group">
                                    <input type="checkbox" id="heritage_listed">
                                    <label for="heritage_listed">Heritage Listed Property</label>
                                </div>
                                <div class="checkbox-group">
                                    <input type="checkbox" id="flood_prone">
                                    <label for="flood_prone">Flood Prone Area</label>
                                </div>
                                <div class="checkbox-group">
                                    <input type="checkbox" id="bushfire_zone">
                                    <label for="bushfire_zone">Bushfire Zone</label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <button type="submit" id="submitBtn">Get Comprehensive AI Analysis</button>
        </form>
        
        <div id="results"></div>
    </div>
    
    <script>
        // Form utility functions
        function toggleLandSize() {
            const propertyType = document.getElementById('property_type').value;
            const landSizeGroup = document.getElementById('land_size_group');
            if (propertyType === 'apartment' || propertyType === 'unit') {
                landSizeGroup.style.display = 'none';
                document.getElementById('land_size_hectares').value = '0';
            } else {
                landSizeGroup.style.display = 'block';
            }
        }

        // Main form submission
        document.getElementById('loanForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Disable submit button
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Analyzing Application...';
            
            // Collect all form data
            const data = {
                // Personal & Financial Details
                annual_income: parseFloat(document.getElementById('annual_income').value),
                employment_type: document.getElementById('employment_type').value,
                employment_months: parseInt(document.getElementById('employment_months').value),
                credit_score: parseInt(document.getElementById('credit_score').value),
                monthly_expenses: parseFloat(document.getElementById('monthly_expenses').value),
                existing_monthly_debts: parseFloat(document.getElementById('existing_monthly_debts').value || 0),
                dependents: parseInt(document.getElementById('dependents').value || 0),
                is_couple: document.getElementById('is_couple').checked,
                first_home_buyer: document.getElementById('first_home_buyer').checked,
                
                // Loan & Property Details
                requested_loan_amount: parseFloat(document.getElementById('requested_loan_amount').value),
                property_value: parseFloat(document.getElementById('property_value').value),
                deposit_amount: parseFloat(document.getElementById('deposit_amount').value),
                loan_term_years: parseInt(document.getElementById('loan_term_years').value),
                property_type: document.getElementById('property_type').value,
                living_area_sqm: parseInt(document.getElementById('living_area_sqm').value),
                postcode: document.getElementById('postcode').value,
                land_size_hectares: parseFloat(document.getElementById('land_size_hectares').value || 0),
                
                // Additional Details
                deposit_source: document.getElementById('deposit_source').value,
                previous_defaults: parseInt(document.getElementById('previous_defaults').value),
                bankruptcy_history: document.getElementById('bankruptcy_history').checked,
                heritage_listed: document.getElementById('heritage_listed').checked,
                flood_prone: document.getElementById('flood_prone').checked,
                bushfire_zone: document.getElementById('bushfire_zone').checked,
                borrowing_history: "good"
            };
            
            // Show loading state
            document.getElementById('results').innerHTML = `
                <div class="loading" style="text-align: center; padding: 60px;">
                    <div style="width: 60px; height: 60px; margin: 0 auto 20px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 2s linear infinite;"></div>
                    <h3 style="color: #667eea; margin-bottom: 15px;">AI Performing Comprehensive Analysis</h3>
                    <p style="color: #666; margin-bottom: 20px;">Analyzing your application across 6 AI components...</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 30px; font-size: 0.9em; color: #888;">
                        <div>- Income Assessment</div>
                        <div>- Property Analysis</div>
                        <div>- Risk Evaluation</div>
                        <div>- LVR Calculation</div>
                        <div>- Serviceability Check</div>
                        <div>- Lender Matching</div>
                    </div>
                </div>
            `;
            
            try {
                const response = await fetch('/api/comprehensive-check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Server error (${response.status}): ${errorText}`);
                }
                
                const result = await response.json();
                displayComprehensiveResults(result, data);
                
            } catch (error) {
                console.error('Analysis error:', error);
                document.getElementById('results').innerHTML = `
                    <div class="error" style="text-align: center; padding: 40px;">
                        <div style="width: 60px; height: 60px; margin: 0 auto 15px; border: 4px solid #f44336; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: #f44336;">!</div>
                        <h3>Analysis Error</h3>
                        <p style="margin: 15px 0;">Network error: ${error.message || 'Failed to connect to analysis server'}</p>
                        <button onclick="location.reload()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Try Again</button>
                    </div>
                `;
            } finally {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
        
        // Comprehensive results display function
        function displayComprehensiveResults(result, applicationData) {
            // Utility functions
            function formatCurrency(amount) {
                return new Intl.NumberFormat('en-AU', {
                    style: 'currency',
                    currency: 'AUD',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(amount);
            }
            
            function getDecisionInfo(decision) {
                const info = {
                    'approved': { color: '#4caf50', icon: 'APPROVED', text: 'APPROVED' },
                    'conditional': { color: '#ff9800', icon: 'CONDITIONAL', text: 'CONDITIONAL APPROVAL' },
                    'declined': { color: '#f44336', icon: 'DECLINED', text: 'DECLINED' },
                    'refer_specialist': { color: '#2196f3', icon: 'SPECIALIST', text: 'REFER TO SPECIALIST' }
                };
                return info[decision] || { color: '#666', icon: 'ANALYSIS', text: decision };
            }
            
            function getRiskColor(grade) {
                const colors = { 'A': '#4caf50', 'B': '#ff9800', 'C': '#f44336', 'DECLINE': '#f44336' };
                return colors[grade] || '#666';
            }
            
            // Calculate LVR from application data
            const lvr = applicationData ? 
                ((applicationData.requested_loan_amount / applicationData.property_value) * 100).toFixed(1) : '0.0';
            
            const decisionInfo = getDecisionInfo(result.decision);
            
            let html = `
                <!-- Decision Header -->
                <div class="analysis-header ${result.decision}" style="background: ${decisionInfo.color};">
                    <div style="font-size: 4em; margin-bottom: 15px;">${decisionInfo.icon}</div>
                    <h2 style="margin: 0; font-size: 2em;">[AI] COMPREHENSIVE AI ANALYSIS COMPLETE</h2>
                    <h3 style="margin: 15px 0; font-size: 1.5em; text-transform: uppercase;">${decisionInfo.text}</h3>
                    <p style="margin: 5px 0; font-size: 1.1em;">
                        Risk Grade: <strong>${result.risk_grade}</strong> | 
                        Confidence: <strong>${(result.overall_confidence * 100).toFixed(0)}%</strong>
                    </p>
                </div>

                <!-- Key Metrics Grid -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h4 style="margin: 0; color: #666; font-size: 0.9em;">LVR</h4>
                        <p style="font-size: 2em; font-weight: bold; margin: 10px 0; color: #333;">${lvr}%</p>
                    </div>
                    <div class="metric-card">
                        <h4 style="margin: 0; color: #666; font-size: 0.9em;">Risk Grade</h4>
                        <p style="font-size: 2em; font-weight: bold; margin: 10px 0; color: ${getRiskColor(result.risk_grade)};">${result.risk_grade}</p>
                    </div>
                    <div class="metric-card">
                        <h4 style="margin: 0; color: #666; font-size: 0.9em;">Max Loan</h4>
                        <p style="font-size: 1.3em; font-weight: bold; margin: 10px 0; color: #333;">${formatCurrency(result.max_loan_amount || 0)}</p>
                    </div>
                    <div class="metric-card">
                        <h4 style="margin: 0; color: #666; font-size: 0.9em;">Est. Rate</h4>
                        <p style="font-size: 2em; font-weight: bold; margin: 10px 0; color: #333;">${(result.estimated_interest_rate || 0).toFixed(2)}%</p>
                    </div>
                </div>
            `;
            
            // Lender Results Section
            if (result.approved_lenders && result.approved_lenders.length > 0) {
                html += `
                    <div class="lender-section">
                        <h3 style="color: #4caf50; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #4caf50; font-weight: bold;">[APPROVED]</span>
                            Approved Lenders (${result.approved_lenders.length})
                        </h3>
                        <div class="lender-badges">
                            ${result.approved_lenders.map(lender => 
                                `<span class="lender-badge approved">${lender}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            if (result.conditional_lenders && result.conditional_lenders.length > 0) {
                html += `
                    <div class="lender-section">
                        <h3 style="color: #ff9800; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #ff9800; font-weight: bold;">[CONDITIONAL]</span>
                            Conditional Approval Lenders (${result.conditional_lenders.length})
                        </h3>
                        <div class="lender-badges">
                            ${result.conditional_lenders.map(lender => 
                                `<span class="lender-badge conditional">${lender}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            if (result.declined_lenders && result.declined_lenders.length > 0 && !result.declined_lenders.includes("All Lenders")) {
                html += `
                    <div class="lender-section">
                        <h3 style="color: #f44336; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #f44336; font-weight: bold;">[DECLINED]</span>
                            Declined Lenders (${result.declined_lenders.length})
                        </h3>
                        <div class="lender-badges">
                            ${result.declined_lenders.map(lender => 
                                `<span class="lender-badge declined">${lender}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            // Analysis Sections
            if (result.key_decision_factors && result.key_decision_factors.length > 0) {
                html += `
                    <div class="analysis-section">
                        <h3 style="color: #333; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #333; font-weight: bold;">[ANALYSIS]</span>
                            Key Decision Factors
                        </h3>
                        <div class="analysis-list">
                            ${result.key_decision_factors.map(factor => 
                                `<div>- ${factor}</div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            if (result.required_conditions && result.required_conditions.length > 0) {
                html += `
                    <div class="analysis-section">
                        <h3 style="color: #ff9800; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #ff9800; font-weight: bold;">[CONDITIONS]</span>
                            Required Conditions
                        </h3>
                        <div class="analysis-list conditions">
                            ${result.required_conditions.map(condition => 
                                `<div>- ${condition}</div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            if (result.recommendations && result.recommendations.length > 0) {
                html += `
                    <div class="analysis-section">
                        <h3 style="color: #2196f3; display: flex; align-items: center;">
                            <span style="margin-right: 10px; color: #2196f3; font-weight: bold;">[RECOMMENDATIONS]</span>
                            AI Recommendations
                        </h3>
                        <div class="analysis-list recommendations">
                            ${result.recommendations.map(rec => 
                                `<div>- ${rec}</div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }

            // Technology Footer
            html += `
                <div style="margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px; text-align: center;">
                    <div style="font-size: 2em; margin-bottom: 15px; color: white; font-weight: bold;">[AI SYSTEM]</div>
                    <h3 style="font-size: 1.8em; margin-bottom: 15px;">Advanced AI Loan Analysis System</h3>
                    <p style="font-size: 1.1em; margin-bottom: 20px;">This comprehensive analysis integrates 6 specialized AI components:</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 25px 0; font-size: 0.95em; font-weight: 500;">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>Income Calculator
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>Property Classifier
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>Risk Scorer
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>LVR Calculator
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>Serviceability Calculator
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <span style="margin-right: 8px; color: #4caf50; font-weight: bold;">[OK]</span>Eligibility Checker
                        </div>
                    </div>
                    <p style="font-size: 0.9em; opacity: 0.9;">Replaces 4+ hours of manual broker work with instant AI-powered analysis</p>
                    <button onclick="location.reload()" style="margin-top: 20px; background: rgba(255,255,255,0.2); color: white; border: 2px solid white; padding: 12px 24px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                        Analyze Another Application
                    </button>
                </div>
            `;

            document.getElementById('results').innerHTML = html;
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
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
    
    def serve_comprehensive_check(self):
        """New comprehensive eligibility check using all backend modules"""
        print("Received comprehensive check request")
        try:
            # Import the comprehensive eligibility checker
            sys.path.append('./src')
            from eligibility_checker import ComprehensiveEligibilityChecker, ComprehensiveLoanApplication
            
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode('utf-8'))
            
            # Convert client data to ComprehensiveLoanApplication
            application = ComprehensiveLoanApplication(
                annual_income=float(client_data.get('annual_income', 0)),
                employment_type=client_data.get('employment_type', 'permanent'),
                employment_months=int(client_data.get('employment_months', 0)),
                credit_score=int(client_data.get('credit_score', 700)),
                monthly_expenses=float(client_data.get('monthly_expenses', 0)),
                existing_monthly_debts=float(client_data.get('existing_monthly_debts', 0)),
                dependents=int(client_data.get('dependents', 0)),
                is_couple=bool(client_data.get('is_couple', False)),
                first_home_buyer=bool(client_data.get('first_home_buyer', False)),
                requested_loan_amount=float(client_data.get('requested_loan_amount', 0)),
                property_value=float(client_data.get('property_value', 0)),
                deposit_amount=float(client_data.get('deposit_amount', 0)),
                loan_term_years=int(client_data.get('loan_term_years', 30)),
                property_type=client_data.get('property_type', 'house'),
                living_area_sqm=int(client_data.get('living_area_sqm', 100)),
                postcode=client_data.get('postcode', '3000'),
                land_size_hectares=float(client_data.get('land_size_hectares', 0)),
                floors_in_building=client_data.get('floors_in_building'),
                units_in_building=client_data.get('units_in_building'),
                heritage_listed=bool(client_data.get('heritage_listed', False)),
                flood_prone=bool(client_data.get('flood_prone', False)),
                bushfire_zone=bool(client_data.get('bushfire_zone', False)),
                previous_defaults=int(client_data.get('previous_defaults', 0)),
                bankruptcy_history=bool(client_data.get('bankruptcy_history', False)),
                deposit_source=client_data.get('deposit_source', 'genuine_savings'),
                borrowing_history=client_data.get('borrowing_history', 'good')
            )
            
            # Run comprehensive eligibility check
            checker = ComprehensiveEligibilityChecker()
            result = checker.check_comprehensive_eligibility(application)
            
            # Convert result to JSON-serializable format
            response_data = {
                "decision": result.decision.value,
                "approved_lenders": result.approved_lenders,
                "declined_lenders": result.declined_lenders,
                "conditional_lenders": result.conditional_lenders,
                "overall_confidence": result.overall_confidence,
                "key_decision_factors": result.key_decision_factors,
                "required_conditions": result.required_conditions,
                "recommendations": result.recommendations,
                "risk_grade": result.risk_grade.value,
                "max_loan_amount": result.max_loan_amount,
                "estimated_interest_rate": result.estimated_interest_rate
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(response_data)
            self.wfile.write(response.encode())
            
        except Exception as e:
            print(f"Comprehensive check error: {e}")  # Debug logging
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({
                "error": f"Comprehensive eligibility check failed: {str(e)}",
                "debug": "Check that all backend modules are properly implemented"
            })
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
    server = HTTPServer(('0.0.0.0', port), LoanHandler)
    
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
    print("   - Professional loan application form")
    print("   - Real-time AI loan matching")
    print("   - 3 ranked loan recommendations")
    print("   - LVR and payment calculations")
    print("   - Beautiful responsive design")
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