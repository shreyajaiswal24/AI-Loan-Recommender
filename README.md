# AI Loan Recommendation System

An intelligent loan recommendation system that analyzes bank documents and provides personalized mortgage recommendations in seconds, replacing manual broker work with AI-powered automation.

## 🎯 Problem Solved

- **Manual Process**: Brokers spend 3-4 hours per client researching loan options
- **Human Labor**: Expensive manual work reading hundreds of bank documents  
- **Scale Limitation**: Human capacity bottleneck
- **Our Solution**: AI system provides recommendations in under 3 seconds with 90%+ accuracy

## 🏗️ Architecture

- **LangChain + RAG**: Intelligent document processing and retrieval
- **Vector Database**: ChromaDB for fast loan product search
- **Anthropic Claude**: Advanced reasoning for loan matching
- **FastAPI**: High-performance backend with web interface
- **Multi-stage AI**: Extraction → Eligibility → Ranking → Recommendations

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Add your ANTHROPIC_API_KEY to .env file
   ```

3. **Create Sample Data**
   ```bash
   cd src/utils
   python sample_data.py
   ```

4. **Run the Application**
   ```bash
   cd src/api
   python main.py
   ```

5. **Access Web Interface**
   - Open http://localhost:8000
   - Fill in client details
   - Get instant loan recommendations

## 📊 Features

### High Accuracy System
- **Multi-stage Validation**: AI double-checks eligibility criteria
- **Confidence Scoring**: Each recommendation includes confidence levels
- **Rule-based + AI Hybrid**: Combines hard rules with intelligent reasoning
- **Continuous Learning**: Improves from broker feedback

### Intelligent Processing
- **Document Intelligence**: Extracts loan terms from bank PDFs
- **Profile Matching**: Matches client financial profile to suitable products  
- **Smart Ranking**: Considers rates, fees, and client-specific factors
- **Real-time Analysis**: Processes all major banks in seconds

### Production Ready
- **FastAPI Backend**: High-performance async API
- **Vector Database**: Scalable document storage and retrieval
- **Error Handling**: Robust error handling and logging
- **Health Monitoring**: Built-in health check endpoints

## 🔧 API Endpoints

### POST /recommend
Get loan recommendations for a client profile.

**Request Body:**
```json
{
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
  "first_home_buyer": true
}
```

**Response:**
```json
{
  "client_profile_summary": {
    "income": 95000,
    "loan_amount": 500000,
    "lvr": 86.2,
    "deposit": 14.7,
    "property_type": "apartment",
    "first_home_buyer": true
  },
  "recommendations": [
    {
      "loan_product": {
        "bank_name": "Commonwealth Bank",
        "product_name": "First Home Buyer Loan",
        "interest_rate": 5.89,
        "comparison_rate": 6.18
      },
      "match_score": 95.0,
      "confidence_score": 92.0,
      "reasoning": "Excellent match for first home buyer...",
      "estimated_monthly_payment": 2847,
      "total_fees_estimate": 1200,
      "warnings": []
    }
  ],
  "processing_time_seconds": 2.34,
  "total_products_analyzed": 15,
  "ai_confidence": "high",
  "broker_review_suggested": false
}
```

### GET /health
System health check.

### POST /feedback
Submit feedback for continuous learning.

## 📁 Project Structure

```
ai_loan_recommender/
├── src/
│   ├── api/           # FastAPI application
│   ├── models/        # Pydantic data models
│   ├── services/      # Core business logic
│   ├── config/        # Configuration settings
│   └── utils/         # Utility functions
├── data/
│   ├── raw/          # Bank documents (PDFs)
│   ├── processed/    # Processed data
│   └── chroma_db/    # Vector database
├── tests/            # Test files
└── docs/             # Documentation
```

## 🔍 How It Works

1. **Document Processing**: 
   - Extracts text from bank loan PDFs
   - Creates embeddings using sentence transformers
   - Stores in ChromaDB vector database

2. **Client Analysis**:
   - Validates client financial profile
   - Calculates key ratios (LVR, DTI)
   - Identifies relevant search criteria

3. **AI Processing**:
   - Retrieves relevant loan documents
   - Extracts structured loan product data
   - Checks eligibility against client profile
   - Ranks products by suitability

4. **Recommendations**:
   - Returns top 3 loan products
   - Includes detailed reasoning
   - Provides confidence scores
   - Suggests broker review if needed

## 🎯 Accuracy Features

- **Structured Extraction**: Converts unstructured bank documents to structured data
- **Multi-pass Validation**: Multiple AI checks for accuracy
- **Confidence Scoring**: Transparent confidence levels for each recommendation
- **Fallback Logic**: Handles edge cases and low-confidence scenarios
- **Human-in-Loop**: Flags uncertain cases for broker review

## 🚀 Deployment

1. **Production Environment**:
   ```bash
   pip install -r requirements.txt
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Docker Deployment**:
   ```dockerfile
   FROM python:3.9-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0"]
   ```

3. **Environment Variables**:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `CHROMA_DB_PATH`: Vector database location
   - `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## 📈 Performance

- **Processing Time**: Under 3 seconds per recommendation
- **Accuracy Target**: 90%+ match with human broker decisions
- **Scalability**: Handles multiple concurrent requests
- **Memory Efficient**: Optimized vector storage and retrieval

## 🔮 Future Enhancements

- **Real-time Rate Updates**: Live bank rate monitoring
- **Advanced Analytics**: Client behavior insights
- **Mobile App**: Native mobile interface
- **Bank API Integration**: Direct bank system connections
- **ML Model Training**: Custom models trained on broker decisions

## 📄 License

This project is proprietary software for loan recommendation automation.

## 🤝 Contributing

This is a commercial project. Contact the development team for contribution guidelines.