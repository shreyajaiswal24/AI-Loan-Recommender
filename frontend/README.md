# AI Loan Recommender Frontend

## React + TypeScript + Tailwind CSS Frontend

This is a modern, comprehensive frontend for the AI Loan Recommender system, built with React, TypeScript, and Tailwind CSS.

## Features

### 🎯 **Complete Integration with Backend**
- ✅ Income Calculator - Multi-employment type income assessment
- ✅ Property Classifier - Smart property categorization  
- ✅ Risk Scoring - A, B, C grade risk assessment
- ✅ LVR Calculator - Lender-specific LVR limits
- ✅ Serviceability Calculator - Income vs expenses analysis
- ✅ Eligibility Checker - Automated approve/decline decisions

### 🎨 **Modern UI/UX**
- Responsive design with Tailwind CSS
- TypeScript for type safety
- Form validation with react-hook-form
- Professional animations and transitions
- Comprehensive results display

### 🚀 **Technology Stack**
- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **Icons**: Heroicons
- **Build Tool**: Create React App

## Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend server running on port 8080

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

### Backend Integration

The frontend expects the backend API at:
- **Development**: http://localhost:8080
- **Production**: Configure in `src/utils/api.ts`

Required backend endpoints:
- `GET /api/health` - Health check
- `POST /api/comprehensive-check` - Main eligibility analysis

## Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── components/
│   │   ├── LoanForm.tsx    # Main application form
│   │   └── ResultsDisplay.tsx # Results visualization
│   ├── types/
│   │   └── index.ts        # TypeScript type definitions
│   ├── utils/
│   │   └── api.ts          # API client and utilities
│   ├── App.tsx            # Main application component
│   ├── index.tsx          # App entry point
│   └── index.css          # Global styles + Tailwind
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind configuration
└── tsconfig.json          # TypeScript configuration
```

## Form Fields

### Personal & Financial Details
- Annual Income (AUD)
- Employment Type (Permanent/Casual/Self-employed/Contract)
- Employment Length (months)
- Credit Score (300-850)
- Monthly Living Expenses (AUD)
- Existing Monthly Debts (AUD)
- Number of Dependents
- Joint Application checkbox
- First Home Buyer checkbox

### Loan & Property Details
- Requested Loan Amount (AUD)
- Property Value (AUD)
- Deposit Amount (AUD)
- Loan Term (15-30 years)
- Property Type (House/Unit/Apartment/etc.)
- Living Area (Square Meters)
- Property Postcode
- Land Size (Hectares)

### Additional Details
- Deposit Source (Genuine Savings/Gift/Equity/Inheritance)
- Previous Credit Defaults (0-3+)
- Previous Bankruptcy checkbox
- Heritage Listed Property checkbox
- Flood Prone Area checkbox

## API Integration

### Request Format
```typescript
interface LoanApplication {
  annual_income: number;
  employment_type: string;
  // ... all form fields
}
```

### Response Format
```typescript
interface EligibilityResult {
  decision: 'approved' | 'conditional' | 'declined' | 'refer_specialist';
  approved_lenders: string[];
  conditional_lenders: string[];
  declined_lenders: string[];
  risk_grade: 'A' | 'B' | 'C' | 'DECLINE';
  max_loan_amount: number;
  estimated_interest_rate: number;
  // ... additional analysis data
}
```

## Build for Production

```bash
# Create production build
npm run build

# Serve built files (example with serve)
npx serve -s build -l 3000
```

## Environment Variables

Create `.env` file for custom configuration:

```env
REACT_APP_API_BASE_URL=http://localhost:8080
REACT_APP_VERSION=1.0.0
```

## Development

### Available Scripts
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Style
- TypeScript strict mode enabled
- ESLint + Prettier configuration
- Tailwind CSS for styling
- Component-based architecture

## Deployment

### Option 1: Static Hosting (Netlify/Vercel)
```bash
npm run build
# Deploy the build/ directory
```

### Option 2: Docker
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on port 8080
   - Check CORS headers in backend
   - Verify API endpoint URLs

2. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npm run build`

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check postcss.config.js and tailwind.config.js

### Debug Mode
Set `NODE_ENV=development` for detailed error messages and debugging information.

## Contributing

1. Follow TypeScript best practices
2. Use Tailwind CSS utility classes
3. Maintain component modularity
4. Add proper error handling
5. Write descriptive commit messages