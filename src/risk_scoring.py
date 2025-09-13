#!/usr/bin/env python3
"""
Risk Scoring System - A, B, C grade classifications for borrower risk assessment
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

class RiskGrade(Enum):
    A_GRADE = "A"
    B_GRADE = "B" 
    C_GRADE = "C"
    DECLINE = "DECLINE"

class CreditScore(Enum):
    EXCELLENT = "excellent"  # 800+
    VERY_GOOD = "very_good"  # 740-799
    GOOD = "good"           # 670-739
    FAIR = "fair"           # 580-669
    POOR = "poor"           # 300-579

@dataclass
class RiskFactors:
    credit_score: int
    employment_stability: str  # "permanent", "casual", "self_employed", "contract"
    employment_months: int
    income_consistency: float  # 0-1 scale
    debt_to_income: float
    loan_to_value: float
    deposit_source: str  # "genuine_savings", "gift", "equity", "inheritance"
    previous_defaults: int
    bankruptcy_history: bool
    property_type: str
    location_risk: str  # "low", "medium", "high"
    borrowing_history: str  # "excellent", "good", "average", "poor"

@dataclass
class RiskAssessment:
    risk_grade: RiskGrade
    risk_score: int  # 1-100 (lower is better)
    grade_confidence: float  # 0-1
    key_strengths: List[str]
    key_weaknesses: List[str]
    recommendations: List[str]
    suitable_lenders: List[str]

class RiskScoringSystem:
    
    def __init__(self):
        # Risk scoring weights
        self.scoring_weights = {
            "credit_score": 0.25,
            "employment_stability": 0.20,
            "debt_to_income": 0.15,
            "loan_to_value": 0.15,
            "deposit_source": 0.10,
            "borrowing_history": 0.10,
            "adverse_events": 0.05
        }
        
        # Grade thresholds (risk scores - lower is better)
        self.grade_thresholds = {
            RiskGrade.A_GRADE: (1, 25),      # Excellent risk
            RiskGrade.B_GRADE: (26, 50),     # Moderate risk
            RiskGrade.C_GRADE: (51, 75),     # Higher risk
            RiskGrade.DECLINE: (76, 100)     # Unacceptable risk
        }
    
    def calculate_credit_score_points(self, credit_score: int) -> Tuple[int, str]:
        """Calculate risk points based on credit score"""
        if credit_score >= 800:
            return 1, "Excellent credit score"
        elif credit_score >= 740:
            return 5, "Very good credit score"
        elif credit_score >= 670:
            return 15, "Good credit score"
        elif credit_score >= 580:
            return 30, "Fair credit score - some lender restrictions"
        else:
            return 50, "Poor credit score - limited lender options"
    
    def calculate_employment_points(self, employment_type: str, months: int) -> Tuple[int, str]:
        """Calculate risk points based on employment stability"""
        base_points = {
            "permanent": 1,
            "contract": 10,
            "casual": 15,
            "self_employed": 20
        }
        
        points = base_points.get(employment_type, 25)
        description = f"{employment_type.replace('_', ' ').title()} employment"
        
        # Adjust for employment duration
        if employment_type == "permanent":
            if months < 3:
                points += 10
                description += " - short tenure"
            elif months >= 24:
                points = max(1, points - 2)
                description += " - strong tenure"
        
        elif employment_type == "self_employed":
            if months < 24:
                points += 15
                description += " - insufficient trading history"
            elif months >= 36:
                points = max(10, points - 5)
                description += " - established business"
        
        elif employment_type == "casual":
            if months < 6:
                points += 10
                description += " - insufficient history"
            elif months >= 12:
                points = max(10, points - 3)
                description += " - consistent casual work"
        
        return points, description
    
    def calculate_dti_points(self, dti_ratio: float) -> Tuple[int, str]:
        """Calculate risk points based on debt-to-income ratio"""
        if dti_ratio <= 3:
            return 1, "Excellent DTI ratio"
        elif dti_ratio <= 4:
            return 5, "Good DTI ratio"
        elif dti_ratio <= 5:
            return 10, "Moderate DTI ratio"
        elif dti_ratio <= 6:
            return 20, "High DTI ratio"
        elif dti_ratio <= 7:
            return 30, "Very high DTI ratio"
        else:
            return 40, "Excessive DTI ratio"
    
    def calculate_lvr_points(self, lvr: float) -> Tuple[int, str]:
        """Calculate risk points based on loan-to-value ratio"""
        if lvr <= 60:
            return 1, "Conservative LVR"
        elif lvr <= 80:
            return 3, "Standard LVR"
        elif lvr <= 85:
            return 8, "Higher LVR - LMI required"
        elif lvr <= 90:
            return 15, "High LVR - significant LMI"
        elif lvr <= 95:
            return 25, "Very high LVR - maximum LMI"
        else:
            return 40, "Excessive LVR - limited lender options"
    
    def calculate_deposit_points(self, deposit_source: str) -> Tuple[int, str]:
        """Calculate risk points based on deposit source"""
        source_points = {
            "genuine_savings": 1,
            "inheritance": 3,
            "equity": 5,
            "gift": 8,
            "loan": 20,
            "unknown": 15
        }
        
        points = source_points.get(deposit_source, 15)
        
        descriptions = {
            "genuine_savings": "Genuine savings - strong financial discipline",
            "inheritance": "Inherited funds - acceptable source",
            "equity": "Property equity - established asset base",
            "gift": "Gift from family - requires documentation",
            "loan": "Borrowed deposit - high risk",
            "unknown": "Unverified deposit source"
        }
        
        return points, descriptions.get(deposit_source, "Unverified deposit source")
    
    def calculate_adverse_points(self, defaults: int, bankruptcy: bool) -> Tuple[int, str]:
        """Calculate risk points for adverse credit events"""
        points = 0
        issues = []
        
        if bankruptcy:
            points += 30
            issues.append("bankruptcy history")
        
        if defaults > 0:
            points += min(defaults * 8, 25)
            issues.append(f"{defaults} previous default(s)")
        
        if not issues:
            return 0, "Clean credit history"
        
        return points, "Adverse credit: " + ", ".join(issues)
    
    def assess_borrower_risk(self, risk_factors: RiskFactors) -> RiskAssessment:
        """Main risk assessment function"""
        
        total_points = 0
        strengths = []
        weaknesses = []
        assessment_details = []
        
        # Credit Score Assessment
        credit_points, credit_desc = self.calculate_credit_score_points(risk_factors.credit_score)
        total_points += credit_points * self.scoring_weights["credit_score"] * 100
        assessment_details.append(credit_desc)
        
        if credit_points <= 5:
            strengths.append(f"Strong credit score ({risk_factors.credit_score})")
        elif credit_points >= 30:
            weaknesses.append(f"Poor credit score ({risk_factors.credit_score})")
        
        # Employment Assessment
        emp_points, emp_desc = self.calculate_employment_points(
            risk_factors.employment_stability, risk_factors.employment_months
        )
        total_points += emp_points * self.scoring_weights["employment_stability"] * 100
        assessment_details.append(emp_desc)
        
        if emp_points <= 5:
            strengths.append("Stable employment history")
        elif emp_points >= 20:
            weaknesses.append("Employment instability concerns")
        
        # DTI Assessment
        dti_points, dti_desc = self.calculate_dti_points(risk_factors.debt_to_income)
        total_points += dti_points * self.scoring_weights["debt_to_income"] * 100
        assessment_details.append(dti_desc)
        
        if dti_points <= 10:
            strengths.append(f"Manageable debt levels (DTI: {risk_factors.debt_to_income:.1f})")
        elif dti_points >= 25:
            weaknesses.append(f"High debt burden (DTI: {risk_factors.debt_to_income:.1f})")
        
        # LVR Assessment
        lvr_points, lvr_desc = self.calculate_lvr_points(risk_factors.loan_to_value)
        total_points += lvr_points * self.scoring_weights["loan_to_value"] * 100
        assessment_details.append(lvr_desc)
        
        if lvr_points <= 8:
            strengths.append(f"Conservative borrowing (LVR: {risk_factors.loan_to_value:.1f}%)")
        elif lvr_points >= 20:
            weaknesses.append(f"High borrowing ratio (LVR: {risk_factors.loan_to_value:.1f}%)")
        
        # Deposit Assessment
        deposit_points, deposit_desc = self.calculate_deposit_points(risk_factors.deposit_source)
        total_points += deposit_points * self.scoring_weights["deposit_source"] * 100
        assessment_details.append(deposit_desc)
        
        if deposit_points <= 5:
            strengths.append("Strong deposit source")
        elif deposit_points >= 15:
            weaknesses.append("Deposit source concerns")
        
        # Adverse Events Assessment
        adverse_points, adverse_desc = self.calculate_adverse_points(
            risk_factors.previous_defaults, risk_factors.bankruptcy_history
        )
        total_points += adverse_points * self.scoring_weights["adverse_events"] * 100
        assessment_details.append(adverse_desc)
        
        if adverse_points == 0:
            strengths.append("Clean credit history")
        elif adverse_points >= 20:
            weaknesses.append("Significant adverse credit history")
        
        # Determine risk grade
        final_score = min(100, max(1, int(total_points)))
        risk_grade = self._determine_grade(final_score)
        
        # Calculate confidence level
        confidence = self._calculate_confidence(risk_factors, final_score)
        
        # Generate recommendations and suitable lenders
        recommendations = self._generate_recommendations(risk_grade, weaknesses)
        suitable_lenders = self._determine_suitable_lenders(risk_grade, risk_factors)
        
        return RiskAssessment(
            risk_grade=risk_grade,
            risk_score=final_score,
            grade_confidence=confidence,
            key_strengths=strengths[:3],  # Top 3 strengths
            key_weaknesses=weaknesses[:3],  # Top 3 weaknesses
            recommendations=recommendations,
            suitable_lenders=suitable_lenders
        )
    
    def _determine_grade(self, score: int) -> RiskGrade:
        """Determine risk grade based on score"""
        for grade, (min_score, max_score) in self.grade_thresholds.items():
            if min_score <= score <= max_score:
                return grade
        return RiskGrade.DECLINE
    
    def _calculate_confidence(self, factors: RiskFactors, score: int) -> float:
        """Calculate confidence level in the risk assessment"""
        confidence_factors = []
        
        # Credit score reliability
        if factors.credit_score > 0:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Employment history completeness
        if factors.employment_months > 0:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.6)
        
        # Income consistency data availability
        confidence_factors.append(max(0.7, factors.income_consistency))
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_recommendations(self, grade: RiskGrade, weaknesses: List[str]) -> List[str]:
        """Generate recommendations based on risk grade and weaknesses"""
        recommendations = []
        
        if grade == RiskGrade.A_GRADE:
            recommendations.append("Excellent risk profile - approach premium lenders for best rates")
            recommendations.append("Consider negotiating rate discounts due to strong profile")
        
        elif grade == RiskGrade.B_GRADE:
            recommendations.append("Good risk profile - suitable for most major lenders")
            if "credit score" in str(weaknesses).lower():
                recommendations.append("Consider improving credit score before applying")
            if "employment" in str(weaknesses).lower():
                recommendations.append("Wait for longer employment history if possible")
        
        elif grade == RiskGrade.C_GRADE:
            recommendations.append("Higher risk profile - consider specialist lenders")
            recommendations.append("Focus on improving weakest risk factors before applying")
            if "debt" in str(weaknesses).lower():
                recommendations.append("Pay down existing debts to improve DTI ratio")
        
        else:  # DECLINE
            recommendations.append("Current profile unlikely to be approved by mainstream lenders")
            recommendations.append("Address major risk factors before reapplying")
            recommendations.append("Consider seeking financial counseling")
        
        return recommendations
    
    def _determine_suitable_lenders(self, grade: RiskGrade, factors: RiskFactors) -> List[str]:
        """Determine which lenders are suitable based on risk grade"""
        if grade == RiskGrade.A_GRADE:
            return ["Great Southern Bank", "Suncorp Bank", "Commonwealth Bank", "Westpac", "ANZ", "NAB"]
        
        elif grade == RiskGrade.B_GRADE:
            lenders = ["Great Southern Bank", "Suncorp Bank", "LaTrobe Financial"]
            if factors.credit_score >= 650:
                lenders.extend(["Commonwealth Bank", "Westpac"])
            return lenders
        
        elif grade == RiskGrade.C_GRADE:
            return ["LaTrobe Financial", "Firstmac", "Liberty Financial"]
        
        else:  # DECLINE
            return []

# Example usage and testing
def test_risk_scoring_system():
    """Test the risk scoring system with different borrower profiles"""
    
    scorer = RiskScoringSystem()
    
    # Test cases
    test_cases = [
        # A-Grade borrower
        RiskFactors(
            credit_score=780,
            employment_stability="permanent",
            employment_months=36,
            income_consistency=0.95,
            debt_to_income=3.2,
            loan_to_value=75,
            deposit_source="genuine_savings",
            previous_defaults=0,
            bankruptcy_history=False,
            property_type="house",
            location_risk="low",
            borrowing_history="excellent"
        ),
        
        # B-Grade borrower
        RiskFactors(
            credit_score=650,
            employment_stability="casual",
            employment_months=18,
            income_consistency=0.80,
            debt_to_income=4.8,
            loan_to_value=85,
            deposit_source="gift",
            previous_defaults=0,
            bankruptcy_history=False,
            property_type="unit",
            location_risk="medium",
            borrowing_history="good"
        ),
        
        # C-Grade borrower
        RiskFactors(
            credit_score=590,
            employment_stability="self_employed",
            employment_months=18,
            income_consistency=0.65,
            debt_to_income=6.2,
            loan_to_value=90,
            deposit_source="equity",
            previous_defaults=1,
            bankruptcy_history=False,
            property_type="unit",
            location_risk="high",
            borrowing_history="average"
        )
    ]
    
    for i, factors in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Credit Score: {factors.credit_score}, Employment: {factors.employment_stability}")
        print(f"DTI: {factors.debt_to_income:.1f}, LVR: {factors.loan_to_value}%")
        print()
        
        assessment = scorer.assess_borrower_risk(factors)
        
        print(f"Risk Assessment Results:")
        print(f"Risk Grade: {assessment.risk_grade.value}")
        print(f"Risk Score: {assessment.risk_score}/100")
        print(f"Confidence: {assessment.grade_confidence:.1%}")
        print()
        
        print("Key Strengths:")
        for strength in assessment.key_strengths:
            print(f"  • {strength}")
        print()
        
        if assessment.key_weaknesses:
            print("Key Weaknesses:")
            for weakness in assessment.key_weaknesses:
                print(f"  • {weakness}")
            print()
        
        print("Recommendations:")
        for rec in assessment.recommendations:
            print(f"  • {rec}")
        print()
        
        print(f"Suitable Lenders: {', '.join(assessment.suitable_lenders)}")
        print("-" * 80)

if __name__ == "__main__":
    test_risk_scoring_system()