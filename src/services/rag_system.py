import logging
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from src.models.client_profile import ClientProfile
from src.models.loan_product import LoanProduct, LoanRecommendation
from src.services.document_processor import DocumentProcessor
from src.config.settings import settings
import json
import re

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.llm = ChatAnthropic(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        self.document_processor = DocumentProcessor()
        self.document_processor.initialize_vector_store()
        
        # Initialize retrieval chain
        self.retriever = self.document_processor.vector_store.as_retriever(
            search_kwargs={"k": settings.max_retrieved_docs}
        )
        
        self.loan_extraction_prompt = self._create_loan_extraction_prompt()
        self.eligibility_check_prompt = self._create_eligibility_prompt()
        self.ranking_prompt = self._create_ranking_prompt()
    
    def _create_loan_extraction_prompt(self) -> PromptTemplate:
        """Create prompt for extracting loan product information"""
        template = """
        You are an expert loan analyst. Extract structured loan product information from the following bank documents.

        Context from bank documents:
        {context}

        Extract all loan products mentioned in the documents. For each product, provide:
        1. Bank name
        2. Product name
        3. Interest rate (current variable/fixed rates)
        4. Comparison rate
        5. Fees (application, ongoing, exit)
        6. Minimum/maximum loan amounts
        7. Maximum LVR (Loan-to-Value Ratio)
        8. Minimum income requirements
        9. Features (offset account, redraw, extra repayments)
        10. Eligibility criteria and restrictions

        Return the information in JSON format as a list of loan products.
        Be precise with numerical values and include all relevant details.
        If information is not explicitly stated, mark as null.

        JSON Response:
        """
        
        return PromptTemplate(
            input_variables=["context"],
            template=template
        )
    
    def _create_eligibility_prompt(self) -> PromptTemplate:
        """Create prompt for checking loan eligibility"""
        template = """
        You are a loan eligibility expert. Analyze if the client meets the requirements for the given loan products.

        Client Profile:
        - Annual Income: ${annual_income:,}
        - Savings/Deposit: ${savings:,}
        - Credit Score: {credit_score}
        - Loan Amount: ${loan_amount:,}
        - Property Value: ${property_value:,}
        - Property Type: {property_type}
        - Employment: {employment_type} for {employment_length_months} months
        - Existing Debts: ${existing_debts:,}
        - Dependents: {dependents}
        - First Home Buyer: {first_home_buyer}
        - LVR: {lvr:.1f}%
        - Deposit: {deposit:.1f}%

        Loan Products to Check:
        {loan_products}

        For each loan product, provide:
        1. Eligibility status (ELIGIBLE/NOT_ELIGIBLE/REQUIRES_REVIEW)
        2. Detailed reasoning
        3. Match score (0-100)
        4. Confidence level (0-100)
        5. Any warnings or concerns
        6. Required actions if not fully eligible

        Focus on:
        - Income requirements
        - LVR limits
        - Employment criteria
        - Deposit requirements
        - Credit score requirements
        - Property type restrictions

        Return as JSON array with detailed analysis for each product.

        JSON Response:
        """
        
        return PromptTemplate(
            input_variables=[
                "annual_income", "savings", "credit_score", "loan_amount", 
                "property_value", "property_type", "employment_type", 
                "employment_length_months", "existing_debts", "dependents",
                "first_home_buyer", "lvr", "deposit", "loan_products"
            ],
            template=template
        )
    
    def _create_ranking_prompt(self) -> PromptTemplate:
        """Create prompt for ranking and final recommendations"""
        template = """
        You are an expert mortgage broker. Rank the eligible loan products and provide top 3 recommendations.

        Client Profile Summary:
        {client_summary}

        Eligible Loan Products with Analysis:
        {eligible_products}

        Ranking Criteria (in order of importance):
        1. Interest rate competitiveness
        2. Total cost (rates + fees)
        3. Client's specific needs and situation
        4. Product features and flexibility
        5. Bank reputation and service

        For the TOP 3 recommendations, provide:
        1. Final ranking (1st, 2nd, 3rd choice)
        2. Key benefits for this client
        3. Estimated monthly payment
        4. Total fees over loan term
        5. Why this product suits the client
        6. Any potential drawbacks

        Consider client's priorities:
        - First home buyer benefits
        - Investment vs owner-occupier
        - Employment type considerations
        - Deposit amount and LVR

        Return JSON with top 3 recommendations and detailed explanations.

        JSON Response:
        """
        
        return PromptTemplate(
            input_variables=["client_summary", "eligible_products"],
            template=template
        )
    
    def extract_loan_products(self, client_profile: ClientProfile) -> List[Dict[str, Any]]:
        """Extract relevant loan products from documents"""
        # Create search query based on client profile
        search_query = self._build_search_query(client_profile)
        
        # Retrieve relevant documents
        relevant_docs = self.document_processor.search_relevant_documents(search_query)
        
        if not relevant_docs:
            raise ValueError("No relevant loan documents found")
        
        # Combine document content
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Extract loan products using LLM
        response = self.llm.invoke(
            self.loan_extraction_prompt.format(context=context)
        )
        
        try:
            # Parse JSON response
            loan_data = json.loads(response.content)
            return loan_data if isinstance(loan_data, list) else [loan_data]
        except json.JSONDecodeError:
            logger.error("Failed to parse loan extraction response")
            return []
    
    def check_eligibility(self, client_profile: ClientProfile, loan_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check client eligibility for loan products"""
        
        response = self.llm.invoke(
            self.eligibility_check_prompt.format(
                annual_income=client_profile.annual_income,
                savings=client_profile.savings,
                credit_score=client_profile.credit_score or "Not provided",
                loan_amount=client_profile.loan_amount,
                property_value=client_profile.property_value,
                property_type=client_profile.property_type.value,
                employment_type=client_profile.employment_type.value,
                employment_length_months=client_profile.employment_length_months,
                existing_debts=client_profile.existing_debts,
                dependents=client_profile.dependents,
                first_home_buyer=client_profile.first_home_buyer,
                lvr=client_profile.loan_to_value_ratio,
                deposit=client_profile.deposit_percentage,
                loan_products=json.dumps(loan_products, indent=2)
            )
        )
        
        try:
            eligibility_results = json.loads(response.content)
            return eligibility_results if isinstance(eligibility_results, list) else [eligibility_results]
        except json.JSONDecodeError:
            logger.error("Failed to parse eligibility response")
            return []
    
    def rank_and_recommend(self, client_profile: ClientProfile, eligible_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank products and generate final recommendations"""
        
        client_summary = {
            "income": client_profile.annual_income,
            "loan_amount": client_profile.loan_amount,
            "lvr": client_profile.loan_to_value_ratio,
            "property_type": client_profile.property_type.value,
            "first_home_buyer": client_profile.first_home_buyer,
            "employment": client_profile.employment_type.value
        }
        
        response = self.llm.invoke(
            self.ranking_prompt.format(
                client_summary=json.dumps(client_summary, indent=2),
                eligible_products=json.dumps(eligible_products, indent=2)
            )
        )
        
        try:
            recommendations = json.loads(response.content)
            return recommendations if isinstance(recommendations, list) else [recommendations]
        except json.JSONDecodeError:
            logger.error("Failed to parse ranking response")
            return []
    
    def _build_search_query(self, client_profile: ClientProfile) -> str:
        """Build search query based on client profile"""
        query_parts = [
            "home loan mortgage interest rates",
            f"{client_profile.property_type.value} property",
        ]
        
        if client_profile.first_home_buyer:
            query_parts.append("first home buyer")
        
        if client_profile.loan_to_value_ratio > 80:
            query_parts.append("high LVR")
        
        if client_profile.employment_type.value in ["self_employed", "contract"]:
            query_parts.append(f"{client_profile.employment_type.value} income")
        
        return " ".join(query_parts)
    
    def get_recommendations(self, client_profile: ClientProfile) -> List[Dict[str, Any]]:
        """Main method to get loan recommendations"""
        try:
            # Extract loan products from documents
            logger.info("Extracting loan products from documents...")
            loan_products = self.extract_loan_products(client_profile)
            
            if not loan_products:
                raise ValueError("No loan products found")
            
            # Check eligibility
            logger.info("Checking eligibility...")
            eligibility_results = self.check_eligibility(client_profile, loan_products)
            
            # Filter eligible products
            eligible_products = [
                result for result in eligibility_results
                if result.get('eligibility_status') in ['ELIGIBLE', 'REQUIRES_REVIEW']
            ]
            
            if not eligible_products:
                raise ValueError("No eligible loan products found")
            
            # Rank and get final recommendations
            logger.info("Ranking and generating recommendations...")
            recommendations = self.rank_and_recommend(client_profile, eligible_products)
            
            # Limit to top 3
            return recommendations[:settings.max_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise