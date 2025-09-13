import React from 'react';
import { EligibilityResult } from '../types';
import { formatCurrency, formatPercentage, calculateLVR } from '../utils/api';

interface ResultsDisplayProps {
  results: EligibilityResult;
  applicationData?: {
    requested_loan_amount: number;
    property_value: number;
  };
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, applicationData }) => {
  const getDecisionColor = (decision: string) => {
    const colors = {
      approved: 'bg-green-500',
      conditional: 'bg-yellow-500',
      declined: 'bg-red-500',
      refer_specialist: 'bg-blue-500',
    };
    return colors[decision as keyof typeof colors] || 'bg-gray-500';
  };

  const getRiskGradeColor = (grade: string) => {
    const colors = {
      A: 'text-green-600',
      B: 'text-yellow-600',
      C: 'text-red-600',
      DECLINE: 'text-red-700',
    };
    return colors[grade as keyof typeof colors] || 'text-gray-600';
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'approved':
        return '✅';
      case 'conditional':
        return '⚠️';
      case 'declined':
        return '❌';
      case 'refer_specialist':
        return '🔄';
      default:
        return '📊';
    }
  };

  const lvr = applicationData 
    ? calculateLVR(applicationData.requested_loan_amount, applicationData.property_value)
    : 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Decision Header */}
      <div className={`${getDecisionColor(results.decision)} text-white rounded-2xl p-8 text-center`}>
        <div className="text-6xl mb-4">{getDecisionIcon(results.decision)}</div>
        <h2 className="text-3xl font-bold mb-2">COMPREHENSIVE AI ANALYSIS COMPLETE</h2>
        <h3 className="text-xl font-semibold uppercase tracking-wide mb-4">
          {results.decision.replace('_', ' ')}
        </h3>
        <p className="text-lg">
          Risk Grade: <span className="font-bold">{results.risk_grade}</span> | 
          Confidence: <span className="font-bold">{formatPercentage(results.overall_confidence * 100, 0)}</span>
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="metric-card text-center">
          <h4 className="text-sm font-medium text-gray-600 mb-2">LVR</h4>
          <p className="text-2xl font-bold text-gray-900">{formatPercentage(lvr)}</p>
        </div>
        <div className="metric-card text-center">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Risk Grade</h4>
          <p className={`text-2xl font-bold ${getRiskGradeColor(results.risk_grade)}`}>
            {results.risk_grade}
          </p>
        </div>
        <div className="metric-card text-center">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Max Loan</h4>
          <p className="text-lg font-bold text-gray-900">
            {formatCurrency(results.max_loan_amount)}
          </p>
        </div>
        <div className="metric-card text-center">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Est. Rate</h4>
          <p className="text-2xl font-bold text-gray-900">
            {formatPercentage(results.estimated_interest_rate, 2)}
          </p>
        </div>
      </div>

      {/* Lender Results */}
      <div className="space-y-6">
        {results.approved_lenders.length > 0 && (
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-green-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Approved Lenders ({results.approved_lenders.length})
            </h3>
            <div className="flex flex-wrap gap-3">
              {results.approved_lenders.map((lender) => (
                <span
                  key={lender}
                  className="bg-green-100 text-green-800 px-4 py-2 rounded-full font-medium"
                >
                  {lender}
                </span>
              ))}
            </div>
          </div>
        )}

        {results.conditional_lenders.length > 0 && (
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-yellow-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Conditional Approval Lenders ({results.conditional_lenders.length})
            </h3>
            <div className="flex flex-wrap gap-3">
              {results.conditional_lenders.map((lender) => (
                <span
                  key={lender}
                  className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full font-medium"
                >
                  {lender}
                </span>
              ))}
            </div>
          </div>
        )}

        {results.declined_lenders.length > 0 && !results.declined_lenders.includes('All Lenders') && (
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-red-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Declined Lenders ({results.declined_lenders.length})
            </h3>
            <div className="flex flex-wrap gap-3">
              {results.declined_lenders.map((lender) => (
                <span
                  key={lender}
                  className="bg-red-100 text-red-800 px-4 py-2 rounded-full font-medium"
                >
                  {lender}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Key Decision Factors */}
      {results.key_decision_factors.length > 0 && (
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Key Decision Factors
          </h3>
          <div className="space-y-3">
            {results.key_decision_factors.map((factor, index) => (
              <div
                key={index}
                className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg"
              >
                <p className="text-gray-800">• {factor}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Required Conditions */}
      {results.required_conditions.length > 0 && (
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-yellow-600 mb-4 flex items-center">
            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Required Conditions
          </h3>
          <div className="space-y-3">
            {results.required_conditions.map((condition, index) => (
              <div
                key={index}
                className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg"
              >
                <p className="text-gray-800">• {condition}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {results.recommendations.length > 0 && (
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-purple-600 mb-4 flex items-center">
            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI Recommendations
          </h3>
          <div className="space-y-3">
            {results.recommendations.map((recommendation, index) => (
              <div
                key={index}
                className="bg-purple-50 border-l-4 border-purple-400 p-4 rounded-r-lg"
              >
                <p className="text-gray-800">• {recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Technology Footer */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl p-8 text-center">
        <div className="text-4xl mb-4">🚀</div>
        <h3 className="text-2xl font-bold mb-4">Advanced AI Loan Analysis</h3>
        <p className="text-lg mb-4">This comprehensive analysis uses 6 AI components:</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm font-medium">
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>Income Calculator
          </div>
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>Property Classifier
          </div>
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>Risk Scorer
          </div>
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>LVR Calculator
          </div>
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>Serviceability Calculator
          </div>
          <div className="flex items-center justify-center">
            <span className="mr-2">✅</span>Eligibility Checker
          </div>
        </div>
        <p className="text-sm mt-6 opacity-90">
          Replaces 4+ hours of manual broker work with instant AI-powered analysis
        </p>
      </div>
    </div>
  );
};

export default ResultsDisplay;