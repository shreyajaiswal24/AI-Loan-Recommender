from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="AI Loan Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClientProfile(BaseModel):
    annual_income: int
    savings: int
    loan_amount: int
    property_value: int
    property_type: str
    employment_type: str
    employment_length_months: int
    credit_score: Optional[int] = None
    existing_debts: int = 0
    dependents: int = 0
    first_home_buyer: bool = False

class LoanProduct(BaseModel):
    bank_name: str
    product_name: str
    interest_rate: float
    comparison_rate: float
    application_fee: int

class LoanRecommendation(BaseModel):
    loan_product: LoanProduct
    match_score: float
    confidence_score: float
    reasoning: str
    estimated_monthly_payment: float
    total_fees_estimate: int
    warnings: List[str]

class RecommendationResponse(BaseModel):
    client_profile_summary: dict
    recommendations: List[LoanRecommendation]
    processing_time_seconds: float
    total_products_analyzed: int
    ai_confidence: str
    broker_review_suggested: bool

@app.get("/")
async def root():
    return {"message": "AI Loan Recommender API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Loan Recommender"}

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(client: ClientProfile):
    # Sample loan products
    LOAN_PRODUCTS = [
        {
            "bank_name": "Commonwealth Bank",
            "product_name": "First Home Buyer Loan",
            "interest_rate": 5.89,
            "comparison_rate": 6.18,
            "application_fee": 0,
            "max_lvr": 95.0,
            "min_income": 60000,
            "first_home_buyer_only": True,
        },
        {
            "bank_name": "ANZ",
            "product_name": "Simplicity Plus",
            "interest_rate": 6.19,
            "comparison_rate": 6.20,
            "application_fee": 799,
            "max_lvr": 90.0,
            "min_income": 50000,
            "first_home_buyer_only": False,
        },
        {
            "bank_name": "Westpac",
            "product_name": "Premier Advantage",
            "interest_rate": 6.09,
            "comparison_rate": 6.18,
            "application_fee": 0,
            "max_lvr": 95.0,
            "min_income": 80000,
            "first_home_buyer_only": False,
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
    
    def score_loan(client, loan):
        score = 100
        reasons = []
        warnings = []
        
        lvr = calculate_lvr(client.loan_amount, client.property_value)
        
        # LVR Check
        if lvr > loan["max_lvr"]:
            score -= 50
            warnings.append(f"LVR {lvr:.1f}% exceeds maximum {loan['max_lvr']}%")
        else:
            reasons.append(f"LVR {lvr:.1f}% within limits")
        
        # Income Check
        if client.annual_income < loan["min_income"]:
            score -= 30
            warnings.append(f"Income below minimum requirement")
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
        match_data = score_loan(client, loan)
        
        if match_data["score"] > 30:
            monthly_payment = calculate_monthly_payment(client.loan_amount, loan["interest_rate"])
            
            loan_product = LoanProduct(
                bank_name=loan["bank_name"],
                product_name=loan["product_name"],
                interest_rate=loan["interest_rate"],
                comparison_rate=loan["comparison_rate"],
                application_fee=loan["application_fee"]
            )
            
            recommendation = LoanRecommendation(
                loan_product=loan_product,
                match_score=match_data["score"],
                confidence_score=match_data["score"] - 10,
                reasoning="; ".join(match_data["reasons"]) if match_data["reasons"] else "Standard loan product",
                estimated_monthly_payment=monthly_payment,
                total_fees_estimate=loan["application_fee"],
                warnings=match_data["warnings"]
            )
            
            scored_loans.append(recommendation)
    
    # Sort by score and take top 3
    scored_loans.sort(key=lambda x: x.match_score, reverse=True)
    top_recommendations = scored_loans[:3]
    
    lvr = calculate_lvr(client.loan_amount, client.property_value)
    deposit = (client.savings / client.property_value) * 100
    
    return RecommendationResponse(
        client_profile_summary={
            "income": client.annual_income,
            "loan_amount": client.loan_amount,
            "lvr": round(lvr, 1),
            "deposit": round(deposit, 1),
            "property_type": client.property_type,
            "first_home_buyer": client.first_home_buyer
        },
        recommendations=top_recommendations,
        processing_time_seconds=2.1,
        total_products_analyzed=len(LOAN_PRODUCTS),
        ai_confidence="high",
        broker_review_suggested=False
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port)