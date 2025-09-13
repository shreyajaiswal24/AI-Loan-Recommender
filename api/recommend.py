from http.server import BaseHTTPRequestHandler
import json

# Loan products data
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
    """Calculate estimated monthly payment"""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(payment, 2)

def calculate_lvr(loan_amount, property_value):
    """Calculate loan-to-value ratio"""
    return (loan_amount / property_value) * 100

def calculate_deposit_percentage(savings, property_value):
    """Calculate deposit percentage"""
    return (savings / property_value) * 100

def score_loan_match(client, loan):
    """AI loan matching logic"""
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
    if client["first_home_buyer"] and loan["first_home_buyer_only"]:
        score += 15
        reasons.append("First home buyer special rate")
    elif not client["first_home_buyer"] and loan["first_home_buyer_only"]:
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

def get_recommendations(client_data):
    """Get AI loan recommendations"""
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
    
    scored_loans.sort(key=lambda x: x["match_score"], reverse=True)
    top_recommendations = scored_loans[:3]
    
    if not top_recommendations:
        raise ValueError("No suitable loan products found")
    
    lvr = calculate_lvr(client_data["loan_amount"], client_data["property_value"])
    deposit = calculate_deposit_percentage(client_data["savings"], client_data["property_value"])
    
    return {
        "client_summary": {
            "income": client_data["annual_income"],
            "loan_amount": client_data["loan_amount"],
            "lvr": round(lvr, 1),
            "deposit": round(deposit, 1),
            "property_type": client_data["property_type"],
            "first_home_buyer": client_data["first_home_buyer"]
        },
        "recommendations": top_recommendations
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()