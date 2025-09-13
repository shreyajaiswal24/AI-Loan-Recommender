#!/usr/bin/env python3
"""
Property Classification System - Categorizes properties for lending eligibility
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

class PropertyCategory(Enum):
    STANDARD_RESIDENTIAL = "standard_residential"
    NON_STANDARD_RESIDENTIAL = "non_standard_residential" 
    UNACCEPTABLE = "unacceptable"

class PropertyType(Enum):
    HOUSE = "house"
    UNIT = "unit"
    TOWNHOUSE = "townhouse"
    VILLA = "villa"
    APARTMENT = "apartment"
    STUDIO_APARTMENT = "studio_apartment"
    RURAL_RESIDENTIAL = "rural_residential"
    VACANT_LAND = "vacant_land"
    WAREHOUSE_CONVERSION = "warehouse_conversion"
    HERITAGE_LISTED = "heritage_listed"

@dataclass
class PropertyDetails:
    property_type: PropertyType
    living_area_sqm: int
    land_size_hectares: float
    property_value: int
    postcode: str
    floors_in_building: Optional[int] = None
    units_in_building: Optional[int] = None
    age_years: Optional[int] = None
    heritage_listed: bool = False
    flood_prone: bool = False
    bushfire_zone: bool = False

@dataclass
class PropertyClassification:
    category: PropertyCategory
    max_lvr: float
    lmi_available: bool
    reasons: List[str]
    warnings: List[str]
    suitable_lenders: List[str]

class PropertyClassifier:
    
    def __init__(self):
        # Studio apartment acceptable postcodes (from Suncorp policy)
        self.studio_acceptable_postcodes = {
            "2010": ["Darlinghurst", "Surry Hills"],
            "2011": ["Elizabeth Bay", "Potts Point", "Rushcutters Bay", "Woolloomooloo"],
            "2021": ["Centennial Park", "Moore Park", "Paddington"]
        }
        
        # High-density property thresholds
        self.high_density_thresholds = {
            "min_floors": 6,
            "min_units": 50
        }
    
    def classify_property(self, property_details: PropertyDetails) -> PropertyClassification:
        """Main classification function"""
        
        # Check for unacceptable properties first
        unacceptable_result = self._check_unacceptable(property_details)
        if unacceptable_result:
            return unacceptable_result
        
        # Check for non-standard properties
        non_standard_result = self._check_non_standard(property_details)
        if non_standard_result:
            return non_standard_result
        
        # Default to standard residential
        return self._classify_standard_residential(property_details)
    
    def _check_unacceptable(self, prop: PropertyDetails) -> Optional[PropertyClassification]:
        """Check if property falls into unacceptable category"""
        
        reasons = []
        warnings = []
        
        # Size requirements
        if prop.property_type in [PropertyType.UNIT, PropertyType.APARTMENT, PropertyType.TOWNHOUSE, PropertyType.VILLA]:
            if prop.living_area_sqm < 40:
                warnings.append(f"Living area {prop.living_area_sqm}m² below minimum 40m²")
                return PropertyClassification(
                    category=PropertyCategory.UNACCEPTABLE,
                    max_lvr=0,
                    lmi_available=False,
                    reasons=["Property size below minimum requirements"],
                    warnings=warnings,
                    suitable_lenders=[]
                )
        
        elif prop.property_type == PropertyType.HOUSE:
            if prop.living_area_sqm < 50:
                warnings.append(f"House living area {prop.living_area_sqm}m² below minimum 50m²")
                return PropertyClassification(
                    category=PropertyCategory.UNACCEPTABLE,
                    max_lvr=0,
                    lmi_available=False,
                    reasons=["House size below minimum requirements"],
                    warnings=warnings,
                    suitable_lenders=[]
                )
        
        # Studio apartments outside acceptable areas
        if prop.property_type == PropertyType.STUDIO_APARTMENT:
            if prop.postcode not in self.studio_acceptable_postcodes:
                return PropertyClassification(
                    category=PropertyCategory.UNACCEPTABLE,
                    max_lvr=0,
                    lmi_available=False,
                    reasons=["Studio apartment in unacceptable location"],
                    warnings=["Studio apartments only accepted in specific Sydney postcodes"],
                    suitable_lenders=[]
                )
        
        # High-value properties (some lenders have limits)
        if prop.property_value > 1800000:
            warnings.append("High-value property may have restricted lender options")
        
        return None
    
    def _check_non_standard(self, prop: PropertyDetails) -> Optional[PropertyClassification]:
        """Check if property is non-standard but still acceptable"""
        
        reasons = []
        warnings = []
        suitable_lenders = []
        max_lvr = 80  # Default for non-standard
        lmi_available = True
        
        # Studio apartments in acceptable areas
        if prop.property_type == PropertyType.STUDIO_APARTMENT:
            if prop.postcode in self.studio_acceptable_postcodes:
                if prop.living_area_sqm >= 35:
                    reasons.append("Studio apartment in acceptable Sydney location")
                    warnings.append("Limited to specific postcodes")
                    max_lvr = 80
                    suitable_lenders = ["Suncorp Bank"]
                    
                    return PropertyClassification(
                        category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                        max_lvr=max_lvr,
                        lmi_available=False,  # Usually no LMI for studios
                        reasons=reasons,
                        warnings=warnings,
                        suitable_lenders=suitable_lenders
                    )
        
        # High-density properties
        if (prop.floors_in_building and prop.floors_in_building >= 6) or \
           (prop.units_in_building and prop.units_in_building > 50):
            reasons.append("High-density property")
            warnings.append("Some lenders may not accept high-density properties")
            max_lvr = 80
            suitable_lenders = ["Suncorp Bank", "LaTrobe Financial"]
            
            return PropertyClassification(
                category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                max_lvr=max_lvr,
                lmi_available=True,
                reasons=reasons,
                warnings=warnings,
                suitable_lenders=suitable_lenders
            )
        
        # Rural residential properties
        if prop.property_type == PropertyType.RURAL_RESIDENTIAL:
            if prop.land_size_hectares <= 10:
                reasons.append("Rural residential under 10 hectares")
                max_lvr = 90
                suitable_lenders = ["Great Southern Bank", "Suncorp Bank"]
            elif prop.land_size_hectares <= 40:
                reasons.append("Rural residential 10-40 hectares")
                warnings.append("Reduced LVR for larger rural properties")
                max_lvr = 70
                suitable_lenders = ["LaTrobe Financial"]
            else:
                reasons.append("Large rural residential property")
                warnings.append("Very limited lender acceptance for properties >40 hectares")
                max_lvr = 60
                suitable_lenders = ["LaTrobe Financial"]
            
            return PropertyClassification(
                category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                max_lvr=max_lvr,
                lmi_available=True,
                reasons=reasons,
                warnings=warnings,
                suitable_lenders=suitable_lenders
            )
        
        # Heritage listed properties
        if prop.heritage_listed:
            reasons.append("Heritage listed property")
            warnings.append("Higher maintenance costs and restrictions apply")
            max_lvr = 70
            suitable_lenders = ["LaTrobe Financial"]
            
            return PropertyClassification(
                category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                max_lvr=max_lvr,
                lmi_available=False,
                reasons=reasons,
                warnings=warnings,
                suitable_lenders=suitable_lenders
            )
        
        # Warehouse conversions
        if prop.property_type == PropertyType.WAREHOUSE_CONVERSION:
            reasons.append("Warehouse conversion to residential")
            warnings.append("Limited lender acceptance")
            max_lvr = 70
            suitable_lenders = ["LaTrobe Financial"]
            
            return PropertyClassification(
                category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                max_lvr=max_lvr,
                lmi_available=True,
                reasons=reasons,
                warnings=warnings,
                suitable_lenders=suitable_lenders
            )
        
        # Environmental risks
        if prop.flood_prone or prop.bushfire_zone:
            risk_type = "flood prone" if prop.flood_prone else "bushfire zone"
            reasons.append(f"Property in {risk_type} area")
            warnings.append(f"May require additional insurance and have reduced LVR")
            max_lvr = 70
            suitable_lenders = ["LaTrobe Financial"]
            
            return PropertyClassification(
                category=PropertyCategory.NON_STANDARD_RESIDENTIAL,
                max_lvr=max_lvr,
                lmi_available=True,
                reasons=reasons,
                warnings=warnings,
                suitable_lenders=suitable_lenders
            )
        
        return None
    
    def _classify_standard_residential(self, prop: PropertyDetails) -> PropertyClassification:
        """Classify as standard residential property"""
        
        reasons = []
        warnings = []
        suitable_lenders = ["Great Southern Bank", "Suncorp Bank", "LaTrobe Financial"]
        
        # Standard house
        if prop.property_type == PropertyType.HOUSE:
            reasons.append("Standard residential house")
            if prop.land_size_hectares <= 2.2:
                reasons.append("Standard residential land size")
            else:
                reasons.append("Large residential block")
                warnings.append("Some lenders may treat as rural residential")
        
        # Standard unit/apartment/townhouse
        elif prop.property_type in [PropertyType.UNIT, PropertyType.APARTMENT, PropertyType.TOWNHOUSE, PropertyType.VILLA]:
            reasons.append(f"Standard {prop.property_type.value}")
            if prop.living_area_sqm >= 40:
                reasons.append(f"Living area {prop.living_area_sqm}m² meets standard requirements")
        
        # Vacant land
        elif prop.property_type == PropertyType.VACANT_LAND:
            if prop.land_size_hectares >= 0.025:  # 250m²
                reasons.append("Standard residential vacant land")
            else:
                warnings.append("Small vacant land may have limited lender acceptance")
        
        # Property value considerations
        if prop.property_value <= 1000000:
            reasons.append("Standard property value range")
        elif prop.property_value <= 1800000:
            reasons.append("Higher value property - most lenders acceptable")
        else:
            warnings.append("High value property may require specialist lending")
            suitable_lenders = ["LaTrobe Financial"]  # Specializes in high-value loans
        
        return PropertyClassification(
            category=PropertyCategory.STANDARD_RESIDENTIAL,
            max_lvr=95,  # Standard maximum with LMI
            lmi_available=True,
            reasons=reasons,
            warnings=warnings,
            suitable_lenders=suitable_lenders
        )
    
    def get_lender_specific_classification(self, prop: PropertyDetails, lender: str) -> Dict:
        """Get specific classification for a particular lender"""
        
        base_classification = self.classify_property(prop)
        
        # Lender-specific adjustments
        if lender == "Great Southern Bank":
            # More conservative on high-density
            if (prop.floors_in_building and prop.floors_in_building >= 6):
                return {
                    "acceptable": False,
                    "reason": "Great Southern Bank does not accept high-density properties"
                }
        
        elif lender == "Suncorp Bank":
            # Accepts studio apartments in specific areas
            if prop.property_type == PropertyType.STUDIO_APARTMENT:
                if prop.postcode in self.studio_acceptable_postcodes:
                    return {
                        "acceptable": True,
                        "max_lvr": 80,
                        "reason": "Studio apartment in acceptable Sydney location"
                    }
        
        elif lender == "LaTrobe Financial":
            # More flexible on property types
            if base_classification.category == PropertyCategory.NON_STANDARD_RESIDENTIAL:
                return {
                    "acceptable": True,
                    "max_lvr": base_classification.max_lvr,
                    "reason": "LaTrobe Financial specializes in non-standard properties"
                }
        
        return {
            "acceptable": base_classification.category != PropertyCategory.UNACCEPTABLE,
            "max_lvr": base_classification.max_lvr,
            "reason": "; ".join(base_classification.reasons)
        }

# Example usage and testing
def test_property_classifier():
    """Test the property classification system"""
    
    classifier = PropertyClassifier()
    
    # Test cases
    test_properties = [
        # Standard house
        PropertyDetails(
            property_type=PropertyType.HOUSE,
            living_area_sqm=120,
            land_size_hectares=0.5,
            property_value=650000,
            postcode="3141"
        ),
        
        # Studio apartment in acceptable area
        PropertyDetails(
            property_type=PropertyType.STUDIO_APARTMENT,
            living_area_sqm=38,
            land_size_hectares=0,
            property_value=450000,
            postcode="2010"
        ),
        
        # High-density unit
        PropertyDetails(
            property_type=PropertyType.UNIT,
            living_area_sqm=65,
            land_size_hectares=0,
            property_value=580000,
            postcode="2000",
            floors_in_building=15,
            units_in_building=80
        ),
        
        # Too small unit
        PropertyDetails(
            property_type=PropertyType.UNIT,
            living_area_sqm=35,
            land_size_hectares=0,
            property_value=400000,
            postcode="3000"
        )
    ]
    
    for i, prop in enumerate(test_properties, 1):
        print(f"Test {i}: {prop.property_type.value}")
        classification = classifier.classify_property(prop)
        
        print(f"  Category: {classification.category.value}")
        print(f"  Max LVR: {classification.max_lvr}%")
        print(f"  LMI Available: {classification.lmi_available}")
        print(f"  Reasons: {'; '.join(classification.reasons)}")
        if classification.warnings:
            print(f"  Warnings: {'; '.join(classification.warnings)}")
        print(f"  Suitable Lenders: {', '.join(classification.suitable_lenders)}")
        print()

if __name__ == "__main__":
    test_property_classifier()