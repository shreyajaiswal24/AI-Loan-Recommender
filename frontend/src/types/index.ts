// API Types
export interface LoanApplication {
  // Personal Details
  annual_income: number;
  employment_type: string;
  employment_months: number;
  credit_score: number;
  monthly_expenses: number;
  existing_monthly_debts: number;
  dependents: number;
  is_couple: boolean;
  first_home_buyer: boolean;
  
  // Loan Details
  requested_loan_amount: number;
  property_value: number;
  deposit_amount: number;
  loan_term_years: number;
  
  // Property Details
  property_type: string;
  living_area_sqm: number;
  postcode: string;
  land_size_hectares: number;
  floors_in_building?: number;
  units_in_building?: number;
  heritage_listed: boolean;
  flood_prone: boolean;
  bushfire_zone: boolean;
  
  // Additional Risk Factors
  previous_defaults: number;
  bankruptcy_history: boolean;
  deposit_source: string;
  borrowing_history: string;
}

export interface EligibilityResult {
  decision: 'approved' | 'conditional' | 'declined' | 'refer_specialist';
  approved_lenders: string[];
  declined_lenders: string[];
  conditional_lenders: string[];
  overall_confidence: number;
  key_decision_factors: string[];
  required_conditions: string[];
  recommendations: string[];
  risk_grade: 'A' | 'B' | 'C' | 'DECLINE';
  max_loan_amount: number;
  estimated_interest_rate: number;
}

// Form Types
export interface FormSection {
  title: string;
  description?: string;
  fields: FormField[];
}

export interface FormField {
  name: keyof LoanApplication;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { value: string | number; label: string }[];
  min?: number;
  max?: number;
  step?: number;
}

// Component Props
export interface ResultCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: 'success' | 'warning' | 'error' | 'info';
  icon?: React.ReactNode;
}

export interface LenderBadgeProps {
  lenders: string[];
  type: 'approved' | 'conditional' | 'declined';
}

export interface AnalysisSection {
  title: string;
  items: string[];
  type: 'factors' | 'conditions' | 'recommendations';
}