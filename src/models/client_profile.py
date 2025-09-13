from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum

class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    INVESTMENT = "investment"

class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time" 
    CASUAL = "casual"
    SELF_EMPLOYED = "self_employed"
    CONTRACT = "contract"

class ClientProfile(BaseModel):
    annual_income: int = Field(..., description="Annual gross income in AUD", ge=1000)
    savings: int = Field(..., description="Total savings/deposit in AUD", ge=0)
    credit_score: Optional[int] = Field(None, description="Credit score (300-850)", ge=300, le=850)
    loan_amount: int = Field(..., description="Requested loan amount in AUD", ge=10000)
    property_value: int = Field(..., description="Property value in AUD", ge=50000)
    property_type: PropertyType = Field(..., description="Type of property")
    employment_type: EmploymentType = Field(..., description="Employment status")
    employment_length_months: int = Field(..., description="Length of current employment in months", ge=0)
    existing_debts: int = Field(0, description="Total existing debts in AUD", ge=0)
    dependents: int = Field(0, description="Number of dependents", ge=0)
    first_home_buyer: bool = Field(False, description="Is this their first home purchase?")
    
    @validator('property_value')
    def property_value_must_exceed_loan(cls, v, values):
        if 'loan_amount' in values and v < values['loan_amount']:
            raise ValueError('Property value must be greater than loan amount')
        return v
    
    @property
    def loan_to_value_ratio(self) -> float:
        """Calculate LVR percentage"""
        return (self.loan_amount / self.property_value) * 100
    
    @property
    def deposit_percentage(self) -> float:
        """Calculate deposit as percentage of property value"""
        return (self.savings / self.property_value) * 100
    
    @property
    def debt_to_income_ratio(self) -> float:
        """Calculate DTI ratio"""
        total_debt = self.loan_amount + self.existing_debts
        return (total_debt / self.annual_income) * 100