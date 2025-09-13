import React, { useState } from 'react';
import LoanForm from './components/LoanForm';
import ResultsDisplay from './components/ResultsDisplay';
import { LoanApplication, EligibilityResult } from './types';
import { checkEligibility } from './utils/api';

function App() {
  const [results, setResults] = useState<EligibilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [applicationData, setApplicationData] = useState<LoanApplication | null>(null);

  const handleFormSubmit = async (data: LoanApplication) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setApplicationData(data);

    try {
      const result = await checkEligibility(data);
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setResults(null);
    setError(null);
    setApplicationData(null);
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <div className="text-6xl mb-4">🤖</div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              AI Loan Recommender
            </h1>
            <p className="text-xl text-gray-600 mb-2">
              Get personalized home loan recommendations powered by AI
            </p>
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                React + TypeScript
              </span>
              <span className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Tailwind CSS
              </span>
              <span className="flex items-center">
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                AI Powered
              </span>
            </div>
          </div>

          {/* Features Overview */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            {[
              { icon: '💰', title: 'Income Calculator', desc: 'Multi-employment types' },
              { icon: '🏠', title: 'Property Classifier', desc: 'Smart categorization' },
              { icon: '⚖️', title: 'Risk Scoring', desc: 'A, B, C grades' },
              { icon: '📊', title: 'LVR Calculator', desc: 'Lender-specific limits' },
              { icon: '💳', title: 'Serviceability', desc: 'Income vs expenses' },
              { icon: '✅', title: 'Eligibility Check', desc: 'Automated decisions' },
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <div className="text-2xl mb-2">{feature.icon}</div>
                <div className="text-sm font-semibold text-gray-900">{feature.title}</div>
                <div className="text-xs text-gray-600">{feature.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        {!results && !loading && (
          <LoanForm onSubmit={handleFormSubmit} isLoading={loading} />
        )}

        {/* Loading State */}
        {loading && (
          <div className="card p-12 text-center">
            <div className="animate-pulse-slow">
              <div className="text-6xl mb-6">🤖</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                AI Performing Comprehensive Analysis
              </h3>
              <p className="text-gray-600 mb-8">
                Analyzing your application across 6 AI components...
              </p>
              <div className="flex justify-center mb-6">
                <svg className="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm text-gray-500">
                <div>✅ Income Assessment</div>
                <div>✅ Property Analysis</div>
                <div>✅ Risk Evaluation</div>
                <div>✅ LVR Calculation</div>
                <div>✅ Serviceability Check</div>
                <div>✅ Lender Matching</div>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="card p-8">
            <div className="text-center">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-2xl font-bold text-red-600 mb-4">Analysis Error</h3>
              <p className="text-gray-700 mb-6">{error}</p>
              <button
                onClick={resetForm}
                className="btn-primary"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {results && applicationData && (
          <div>
            <ResultsDisplay 
              results={results} 
              applicationData={{
                requested_loan_amount: applicationData.requested_loan_amount,
                property_value: applicationData.property_value
              }}
            />
            <div className="text-center mt-8">
              <button
                onClick={resetForm}
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
              >
                Analyze Another Application
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 text-sm">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <p className="mb-2">
              <strong>AI Loan Recommender</strong> - Built with React, TypeScript & Tailwind CSS
            </p>
            <p>
              Powered by advanced AI algorithms analyzing real Australian lending criteria
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;