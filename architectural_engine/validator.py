"""
Design validation module to ensure feasibility and compliance.
"""

from typing import List, NamedTuple
from .schemas import DesignInput, BuildingType

class ValidationResult(NamedTuple):
    """Result of design validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class DesignValidator:
    """Validates architectural design inputs and constraints."""
    
    # Minimum plot sizes for different building types (in sq.ft)
    MIN_PLOT_SIZES = {
        BuildingType.INDEPENDENT_HOUSE: 600,
        BuildingType.DUPLEX: 800,
        BuildingType.VILLA: 1500,
        BuildingType.ROW_HOUSE: 400,
        BuildingType.APARTMENT: 300
    }
    
    def validate_design_feasibility(self, input_data: DesignInput) -> ValidationResult:
        """
        Validate if the design is feasible with given constraints.
        
        Args:
            input_data: Design input parameters
            
        Returns:
            ValidationResult: Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # Validate plot size
        min_size = self.MIN_PLOT_SIZES.get(input_data.building_type, 600)
        if input_data.land_size < min_size:
            errors.append(f"Plot size {input_data.land_size} sq.ft is too small for {input_data.building_type.value}. Minimum required: {min_size} sq.ft")
        
        # Validate bedroom configuration vs plot size
        bedrooms_count = int(input_data.bedroom_config[:-3])
        if self._is_bedroom_count_excessive(bedrooms_count, input_data.land_size):
            errors.append(f"{bedrooms_count} bedrooms may not fit comfortably in {input_data.land_size} sq.ft plot")
        
        # Validate floors vs building type
        if input_data.building_type == BuildingType.APARTMENT and input_data.floors > 1:
            warnings.append("Apartment units are typically single floor. Consider Independent House or Duplex for multi-floor design")
        
        # Validate staircase requirement
        if input_data.floors > 1 and input_data.staircase_type is None:
            errors.append("Staircase type must be specified for multi-floor buildings")
        
        if input_data.floors == 1 and input_data.staircase_type is not None:
            warnings.append("Staircase specified for single floor building - will be ignored")
        
        # Validate plot dimensions (assuming square plot for simplicity)
        plot_side = input_data.land_size ** 0.5
        if plot_side < 20:  # Less than 20 feet side
            warnings.append("Very narrow plot may limit design flexibility")
        
        # Check for very large plots with small bedroom count
        if input_data.land_size > 3000 and bedrooms_count < 3:
            warnings.append("Large plot with few bedrooms - consider additional amenities or larger rooms")
        
        # Validate special requirements
        if input_data.special_requirements:
            for requirement in input_data.special_requirements:
                if requirement.lower() in ['swimming pool', 'tennis court'] and input_data.land_size < 2000:
                    warnings.append(f"Plot may be too small for {requirement}")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def _is_bedroom_count_excessive(self, bedrooms_count: int, land_size: float) -> bool:
        """Check if bedroom count is excessive for the given land size."""
        # Rule of thumb: minimum 300 sq.ft per bedroom including common areas
        min_area_required = bedrooms_count * 300
        return min_area_required > land_size * 0.8  # 80% of land can be built upon
    
    def validate_room_dimensions(self, room_name: str, length: float, width: float) -> ValidationResult:
        """Validate individual room dimensions."""
        errors = []
        warnings = []
        
        area = length * width
        
        # Minimum room size requirements
        min_requirements = {
            'living_room': {'min_area': 120, 'min_width': 10},
            'master_bedroom': {'min_area': 120, 'min_width': 10},
            'bedroom': {'min_area': 80, 'min_width': 8},
            'kitchen': {'min_area': 60, 'min_width': 6},
            'bathroom': {'min_area': 25, 'min_width': 4},
            'balcony': {'min_area': 30, 'min_width': 4}
        }
        
        room_type = room_name.lower().replace('_', ' ')
        for key, requirements in min_requirements.items():
            if key in room_type:
                if area < requirements['min_area']:
                    errors.append(f"{room_name} area {area} sq.ft is below minimum {requirements['min_area']} sq.ft")
                
                if min(length, width) < requirements['min_width']:
                    errors.append(f"{room_name} minimum dimension {min(length, width)} ft is below required {requirements['min_width']} ft")
                break
        
        # Check aspect ratio
        aspect_ratio = max(length, width) / min(length, width)
        if aspect_ratio > 3:
            warnings.append(f"{room_name} has excessive aspect ratio {aspect_ratio:.1f}:1 - may feel narrow")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
