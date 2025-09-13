import React from 'react';
import { useForm } from 'react-hook-form';
import { LoanApplication } from '../types';
import { validatePostcode } from '../utils/api';

interface LoanFormProps {
  onSubmit: (data: LoanApplication) => void;
  isLoading?: boolean;
}

const LoanForm: React.FC<LoanFormProps> = ({ onSubmit, isLoading = false }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoanApplication>({
    defaultValues: {
      credit_score: 700,
      dependents: 0,
      is_couple: false,
      first_home_buyer: false,
      loan_term_years: 30,
      land_size_hectares: 0,
      heritage_listed: false,
      flood_prone: false,
      bushfire_zone: false,
      previous_defaults: 0,
      bankruptcy_history: false,
      deposit_source: 'genuine_savings',
      borrowing_history: 'good',
      existing_monthly_debts: 0,
    },
  });

  const propertyType = watch('property_type');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Personal & Financial Details */}
      <div className="card p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="bg-primary-100 rounded-full p-2 mr-3">
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          Personal & Financial Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Annual Income (AUD) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.annual_income ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 95,000"
              {...register('annual_income', {
                required: 'Annual income is required',
                min: { value: 30000, message: 'Minimum income is $30,000' },
              })}
            />
            {errors.annual_income && (
              <p className="mt-1 text-sm text-red-600">{errors.annual_income.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employment Type *
            </label>
            <select
              className={`form-select ${errors.employment_type ? 'border-red-500 ring-red-500' : ''}`}
              {...register('employment_type', { required: 'Employment type is required' })}
            >
              <option value="">Select employment type...</option>
              <option value="permanent">Permanent Full Time</option>
              <option value="casual">Casual</option>
              <option value="self_employed">Self Employed</option>
              <option value="contract">Contract</option>
            </select>
            {errors.employment_type && (
              <p className="mt-1 text-sm text-red-600">{errors.employment_type.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employment Length (months) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.employment_months ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 18"
              {...register('employment_months', {
                required: 'Employment length is required',
                min: { value: 0, message: 'Cannot be negative' },
              })}
            />
            {errors.employment_months && (
              <p className="mt-1 text-sm text-red-600">{errors.employment_months.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Credit Score *
            </label>
            <input
              type="number"
              className={`form-input ${errors.credit_score ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 750"
              {...register('credit_score', {
                required: 'Credit score is required',
                min: { value: 300, message: 'Minimum credit score is 300' },
                max: { value: 850, message: 'Maximum credit score is 850' },
              })}
            />
            {errors.credit_score && (
              <p className="mt-1 text-sm text-red-600">{errors.credit_score.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monthly Living Expenses (AUD) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.monthly_expenses ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 3,500"
              {...register('monthly_expenses', {
                required: 'Monthly expenses are required',
                min: { value: 1000, message: 'Minimum expenses are $1,000' },
              })}
            />
            {errors.monthly_expenses && (
              <p className="mt-1 text-sm text-red-600">{errors.monthly_expenses.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Existing Monthly Debts (AUD)
            </label>
            <input
              type="number"
              className="form-input"
              placeholder="e.g., 800"
              {...register('existing_monthly_debts', {
                min: { value: 0, message: 'Cannot be negative' },
              })}
            />
            {errors.existing_monthly_debts && (
              <p className="mt-1 text-sm text-red-600">{errors.existing_monthly_debts.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Dependents
            </label>
            <input
              type="number"
              className="form-input"
              placeholder="0"
              {...register('dependents', {
                min: { value: 0, message: 'Cannot be negative' },
                max: { value: 10, message: 'Maximum 10 dependents' },
              })}
            />
          </div>

          <div className="md:col-span-2">
            <div className="flex items-center space-x-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 mr-2"
                  {...register('is_couple')}
                />
                <span className="text-sm font-medium text-gray-700">Joint Application (Couple)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 mr-2"
                  {...register('first_home_buyer')}
                />
                <span className="text-sm font-medium text-gray-700">First Home Buyer</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Loan & Property Details */}
      <div className="card p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="bg-green-100 rounded-full p-2 mr-3">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7zm0 0V5a2 2 0 012-2h6l2 2h6a2 2 0 012 2v2H3z" />
            </svg>
          </div>
          Loan & Property Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Requested Loan Amount (AUD) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.requested_loan_amount ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 500,000"
              {...register('requested_loan_amount', {
                required: 'Loan amount is required',
                min: { value: 10000, message: 'Minimum loan amount is $10,000' },
              })}
            />
            {errors.requested_loan_amount && (
              <p className="mt-1 text-sm text-red-600">{errors.requested_loan_amount.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Property Value (AUD) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.property_value ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 650,000"
              {...register('property_value', {
                required: 'Property value is required',
                min: { value: 50000, message: 'Minimum property value is $50,000' },
              })}
            />
            {errors.property_value && (
              <p className="mt-1 text-sm text-red-600">{errors.property_value.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deposit Amount (AUD) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.deposit_amount ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 130,000"
              {...register('deposit_amount', {
                required: 'Deposit amount is required',
                min: { value: 0, message: 'Cannot be negative' },
              })}
            />
            {errors.deposit_amount && (
              <p className="mt-1 text-sm text-red-600">{errors.deposit_amount.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Loan Term (years) *
            </label>
            <select
              className="form-select"
              {...register('loan_term_years', { required: 'Loan term is required' })}
            >
              <option value={30}>30 years</option>
              <option value={25}>25 years</option>
              <option value={20}>20 years</option>
              <option value={15}>15 years</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Property Type *
            </label>
            <select
              className={`form-select ${errors.property_type ? 'border-red-500 ring-red-500' : ''}`}
              {...register('property_type', { required: 'Property type is required' })}
            >
              <option value="">Select property type...</option>
              <option value="house">House</option>
              <option value="unit">Unit</option>
              <option value="apartment">Apartment</option>
              <option value="townhouse">Townhouse</option>
              <option value="villa">Villa</option>
              <option value="studio_apartment">Studio Apartment</option>
              <option value="rural_residential">Rural Residential</option>
            </select>
            {errors.property_type && (
              <p className="mt-1 text-sm text-red-600">{errors.property_type.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Living Area (Square Meters) *
            </label>
            <input
              type="number"
              className={`form-input ${errors.living_area_sqm ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 120"
              {...register('living_area_sqm', {
                required: 'Living area is required',
                min: { value: 20, message: 'Minimum living area is 20m²' },
              })}
            />
            {errors.living_area_sqm && (
              <p className="mt-1 text-sm text-red-600">{errors.living_area_sqm.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Property Postcode *
            </label>
            <input
              type="text"
              className={`form-input ${errors.postcode ? 'border-red-500 ring-red-500' : ''}`}
              placeholder="e.g., 3141"
              maxLength={4}
              {...register('postcode', {
                required: 'Postcode is required',
                validate: (value) => validatePostcode(value) || 'Invalid Australian postcode',
              })}
            />
            {errors.postcode && (
              <p className="mt-1 text-sm text-red-600">{errors.postcode.message}</p>
            )}
          </div>

          {propertyType !== 'apartment' && propertyType !== 'unit' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Land Size (Hectares)
              </label>
              <input
                type="number"
                step="0.01"
                className="form-input"
                placeholder="e.g., 0.5"
                {...register('land_size_hectares', {
                  min: { value: 0, message: 'Cannot be negative' },
                })}
              />
            </div>
          )}
        </div>
      </div>

      {/* Additional Details */}
      <div className="card p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="bg-blue-100 rounded-full p-2 mr-3">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          Additional Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deposit Source *
            </label>
            <select
              className="form-select"
              {...register('deposit_source', { required: 'Deposit source is required' })}
            >
              <option value="genuine_savings">Genuine Savings</option>
              <option value="gift">Gift from Family</option>
              <option value="equity">Property Equity</option>
              <option value="inheritance">Inheritance</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Previous Credit Defaults *
            </label>
            <select
              className="form-select"
              {...register('previous_defaults', { required: 'Credit history is required' })}
            >
              <option value={0}>None</option>
              <option value={1}>1 Default</option>
              <option value={2}>2 Defaults</option>
              <option value={3}>3+ Defaults</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <div className="flex items-center space-x-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500 mr-2"
                  {...register('bankruptcy_history')}
                />
                <span className="text-sm font-medium text-gray-700">Previous Bankruptcy</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500 mr-2"
                  {...register('heritage_listed')}
                />
                <span className="text-sm font-medium text-gray-700">Heritage Listed Property</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500 mr-2"
                  {...register('flood_prone')}
                />
                <span className="text-sm font-medium text-gray-700">Flood Prone Area</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-center">
        <button
          type="submit"
          disabled={isLoading}
          className={`btn-primary px-8 py-4 text-lg font-bold ${
            isLoading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isLoading ? (
            <div className="flex items-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing Application...
            </div>
          ) : (
            '🤖 Get Comprehensive AI Analysis'
          )}
        </button>
      </div>
    </form>
  );
};

export default LoanForm;