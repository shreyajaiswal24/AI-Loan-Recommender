from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import time
import logging
from typing import List, Dict, Any
from src.models.client_profile import ClientProfile
from src.models.loan_product import RecommendationResponse, LoanRecommendation, LoanProduct
from src.services.rag_system import RAGSystem
from src.config.settings import settings
import uvicorn

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered loan recommendation system that analyzes bank documents and provides personalized mortgage recommendations"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    try:
        logger.info("Initializing RAG system...")
        rag_system = RAGSystem()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Loan Recommender</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .recommendations { margin-top: 30px; }
            .loan-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 15px 0; background: #f9f9f9; }
            .loading { text-align: center; color: #666; }
            .error { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>AI Loan Recommendation System</h1>
        <p>Get personalized home loan recommendations in seconds</p>
        
        <form id="loanForm">
            <div class="form-group">
                <label for="annual_income">Annual Income (AUD)</label>
                <input type="number" id="annual_income" required min="1000">
            </div>
            
            <div class="form-group">
                <label for="savings">Savings/Deposit (AUD)</label>
                <input type="number" id="savings" required min="0">
            </div>
            
            <div class="form-group">
                <label for="loan_amount">Loan Amount (AUD)</label>
                <input type="number" id="loan_amount" required min="10000">
            </div>
            
            <div class="form-group">
                <label for="property_value">Property Value (AUD)</label>
                <input type="number" id="property_value" required min="50000">
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
                <input type="number" id="employment_length_months" required min="0">
            </div>
            
            <div class="form-group">
                <label for="credit_score">Credit Score (optional)</label>
                <input type="number" id="credit_score" min="300" max="850">
            </div>
            
            <div class="form-group">
                <label for="existing_debts">Existing Debts (AUD)</label>
                <input type="number" id="existing_debts" value="0" min="0">
            </div>
            
            <div class="form-group">
                <label for="dependents">Number of Dependents</label>
                <input type="number" id="dependents" value="0" min="0">
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="first_home_buyer"> First Home Buyer
                </label>
            </div>
            
            <button type="submit">Get Loan Recommendations</button>
        </form>
        
        <div id="results" class="recommendations"></div>
        
        <script>
            document.getElementById('loanForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {};
                
                // Collect form data
                data.annual_income = parseInt(formData.get('annual_income') || document.getElementById('annual_income').value);
                data.savings = parseInt(formData.get('savings') || document.getElementById('savings').value);
                data.loan_amount = parseInt(formData.get('loan_amount') || document.getElementById('loan_amount').value);
                data.property_value = parseInt(formData.get('property_value') || document.getElementById('property_value').value);
                data.property_type = formData.get('property_type') || document.getElementById('property_type').value;
                data.employment_type = formData.get('employment_type') || document.getElementById('employment_type').value;
                data.employment_length_months = parseInt(formData.get('employment_length_months') || document.getElementById('employment_length_months').value);
                data.existing_debts = parseInt(formData.get('existing_debts') || document.getElementById('existing_debts').value || 0);
                data.dependents = parseInt(formData.get('dependents') || document.getElementById('dependents').value || 0);
                data.first_home_buyer = document.getElementById('first_home_buyer').checked;
                
                const creditScore = document.getElementById('credit_score').value;
                if (creditScore) data.credit_score = parseInt(creditScore);
                
                // Show loading
                document.getElementById('results').innerHTML = '<div class="loading">Analyzing loan options... This may take a few seconds.</div>';
                
                try {
                    const response = await fetch('/recommend', {
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
                    document.getElementById('results').innerHTML = `<div class="error">Error: ${error.message}</div>`;
                }
            });
            
            function displayResults(data) {
                let html = '<h2>Loan Recommendations</h2>';
                html += `<p>Analysis completed in ${data.processing_time_seconds.toFixed(2)} seconds</p>`;
                html += `<p>Analyzed ${data.total_products_analyzed} loan products</p>`;
                html += `<p>AI Confidence: ${data.ai_confidence}</p>`;
                
                if (data.broker_review_suggested) {
                    html += '<p style="color: orange;"><strong>⚠️ Broker review suggested for optimal results</strong></p>';
                }
                
                data.recommendations.forEach((rec, index) => {
                    html += `
                        <div class="loan-card">
                            <h3>#${index + 1} - ${rec.loan_product.bank_name} - ${rec.loan_product.product_name}</h3>
                            <p><strong>Interest Rate:</strong> ${rec.loan_product.interest_rate}% (Comparison: ${rec.loan_product.comparison_rate}%)</p>
                            <p><strong>Estimated Monthly Payment:</strong> $${rec.estimated_monthly_payment.toLocaleString()}</p>
                            <p><strong>Total Fees Estimate:</strong> $${rec.total_fees_estimate.toLocaleString()}</p>
                            <p><strong>Match Score:</strong> ${rec.match_score}%</p>
                            <p><strong>Confidence:</strong> ${rec.confidence_score}%</p>
                            <p><strong>Why this loan:</strong> ${rec.reasoning}</p>
                            ${rec.warnings.length > 0 ? `<p style="color: orange;"><strong>Warnings:</strong> ${rec.warnings.join(', ')}</p>` : ''}
                        </div>
                    `;
                });
                
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/recommend", response_model=RecommendationResponse)
async def get_loan_recommendations(client_profile: ClientProfile):
    """Get AI-powered loan recommendations"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing recommendation request for client with income ${client_profile.annual_income:,}")
        
        # Get recommendations from RAG system
        raw_recommendations = rag_system.get_recommendations(client_profile)
        
        # Convert to proper response format
        recommendations = []
        for rec_data in raw_recommendations:
            try:
                # Create LoanProduct from recommendation data
                loan_product = LoanProduct(
                    id=rec_data.get('id', 'unknown'),
                    bank_name=rec_data.get('bank_name', 'Unknown Bank'),
                    product_name=rec_data.get('product_name', 'Unknown Product'),
                    loan_type=rec_data.get('loan_type', 'variable'),
                    interest_rate=rec_data.get('interest_rate', 0.0),
                    comparison_rate=rec_data.get('comparison_rate', 0.0),
                    application_fee=rec_data.get('application_fee'),
                    ongoing_fee=rec_data.get('ongoing_fee'),
                    exit_fee=rec_data.get('exit_fee'),
                    min_loan_amount=rec_data.get('min_loan_amount', 50000),
                    max_loan_amount=rec_data.get('max_loan_amount', 2000000),
                    max_lvr=rec_data.get('max_lvr', 95.0),
                    min_income=rec_data.get('min_income'),
                    offset_account=rec_data.get('offset_account', False),
                    redraw_facility=rec_data.get('redraw_facility', False),
                    extra_repayments=rec_data.get('extra_repayments', True),
                    first_home_buyer_only=rec_data.get('first_home_buyer_only', False),
                    investment_property_allowed=rec_data.get('investment_property_allowed', True),
                    self_employed_accepted=rec_data.get('self_employed_accepted', True)
                )
                
                # Create recommendation
                recommendation = LoanRecommendation(
                    loan_product=loan_product,
                    match_score=rec_data.get('match_score', 0.0),
                    confidence_score=rec_data.get('confidence_score', 0.0),
                    reasoning=rec_data.get('reasoning', 'AI-generated recommendation'),
                    estimated_monthly_payment=rec_data.get('estimated_monthly_payment', 0.0),
                    total_fees_estimate=rec_data.get('total_fees_estimate', 0.0),
                    eligibility_check=rec_data.get('eligibility_check', {}),
                    warnings=rec_data.get('warnings', [])
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to parse recommendation: {str(e)}")
                continue
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No suitable loan products found")
        
        processing_time = time.time() - start_time
        
        # Determine overall confidence
        avg_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
        if avg_confidence >= settings.high_confidence_threshold:
            ai_confidence = "high"
            broker_review = False
        elif avg_confidence >= settings.min_confidence_score:
            ai_confidence = "medium"
            broker_review = False
        else:
            ai_confidence = "low"
            broker_review = True
        
        response = RecommendationResponse(
            client_profile_summary={
                "income": client_profile.annual_income,
                "loan_amount": client_profile.loan_amount,
                "lvr": round(client_profile.loan_to_value_ratio, 1),
                "deposit": round(client_profile.deposit_percentage, 1),
                "property_type": client_profile.property_type.value,
                "first_home_buyer": client_profile.first_home_buyer
            },
            recommendations=recommendations,
            processing_time_seconds=processing_time,
            total_products_analyzed=len(raw_recommendations),
            ai_confidence=ai_confidence,
            broker_review_suggested=broker_review
        )
        
        logger.info(f"Successfully generated {len(recommendations)} recommendations in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_system_initialized": rag_system is not None,
        "version": settings.app_version
    }

@app.post("/feedback")
async def submit_feedback(feedback_data: dict):
    """Submit feedback for continuous learning"""
    # TODO: Implement feedback storage and processing
    logger.info(f"Received feedback: {feedback_data}")
    return {"status": "feedback_received", "message": "Thank you for your feedback"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )