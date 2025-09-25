"""
JSON schemas and data structures for architectural design inputs and outputs.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum

class FacingDirection(str, Enum):
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NORTHEAST = "Northeast"
    NORTHWEST = "Northwest"
    SOUTHEAST = "Southeast"
    SOUTHWEST = "Southwest"

class BuildingType(str, Enum):
    INDEPENDENT_HOUSE = "Independent House"
    ROW_HOUSE = "Row House"
    DUPLEX = "Duplex"
    VILLA = "Villa"
    APARTMENT = "Apartment"

class StaircaseType(str, Enum):
    STRAIGHT = "Straight"
    L_SHAPED = "L-Shaped"
    U_SHAPED = "U-Shaped"
    SPIRAL = "Spiral"
    WINDER = "Winder"

class DesignInput(BaseModel):
    """Input schema for architectural design generation."""
    land_size: float = Field(..., gt=0, description="Land size in square feet")
    facing: FacingDirection = Field(..., description="Building orientation/facing direction")
    building_type: BuildingType = Field(..., description="Type of building")
    bedroom_config: str = Field(..., pattern=r"^\d+BHK$", description="Bedroom configuration (e.g., 2BHK, 3BHK)")
    staircase_type: StaircaseType = Field(..., description="Type of staircase")
    floors: int = Field(default=1, ge=1, le=3, description="Number of floors")
    budget_range: Optional[str] = Field(None, description="Budget range (Low/Medium/High)")
    special_requirements: Optional[List[str]] = Field(default=[], description="Special requirements")
    
    @validator('bedroom_config')
    def validate_bedroom_config(cls, v):
        if not v.endswith('BHK'):
            raise ValueError('Bedroom configuration must end with BHK')
        try:
            bedrooms = int(v[:-3])
            if bedrooms < 1 or bedrooms > 5:
                raise ValueError('Number of bedrooms must be between 1 and 5')
        except ValueError:
            raise ValueError('Invalid bedroom configuration format')
        return v

class Setbacks(BaseModel):
    """Setback requirements."""
    front: float = Field(..., ge=0, description="Front setback in feet")
    rear: float = Field(..., ge=0, description="Rear setback in feet")
    left: float = Field(..., ge=0, description="Left side setback in feet")
    right: float = Field(..., ge=0, description="Right side setback in feet")

class RoomAllocation(BaseModel):
    """Room-wise area allocation."""
    living_room: float = Field(..., gt=0, description="Living room area in sq.ft")
    kitchen: float = Field(..., gt=0, description="Kitchen area in sq.ft")
    bedrooms: Dict[str, float] = Field(..., description="Bedroom areas in sq.ft")
    bathrooms: Dict[str, float] = Field(..., description="Bathroom areas in sq.ft")
    balcony: float = Field(default=0, ge=0, description="Balcony area in sq.ft")
    corridors: float = Field(..., gt=0, description="Corridor/circulation area in sq.ft")
    staircase: float = Field(default=0, ge=0, description="Staircase area in sq.ft")
    parking: float = Field(default=0, ge=0, description="Parking area in sq.ft")
    utility: float = Field(default=0, ge=0, description="Utility/store area in sq.ft")
    pooja_room: float = Field(default=0, ge=0, description="Pooja room area in sq.ft")

class StructuralRecommendations(BaseModel):
    """Structural and circulation recommendations."""
    foundation_type: str = Field(..., description="Recommended foundation type")
    wall_material: str = Field(..., description="Recommended wall material")
    roofing_system: str = Field(..., description="Recommended roofing system")
    ventilation_strategy: str = Field(..., description="Ventilation strategy")
    natural_light_optimization: str = Field(..., description="Natural light optimization")
    circulation_flow: str = Field(..., description="Circulation flow recommendations")

class DesignRationale(BaseModel):
    """Design rationale and explanations."""
    orientation_benefits: str = Field(..., description="Benefits of chosen orientation")
    ventilation_strategy: str = Field(..., description="Ventilation and light optimization")
    vastu_compliance: str = Field(..., description="Vastu/Feng Shui principles applied")
    zoning_compliance: str = Field(..., description="Local zoning norms compliance")
    expansion_potential: str = Field(..., description="Future expansion possibilities")
    sustainability_features: List[str] = Field(default=[], description="Sustainability features")

class SpaceEfficiency(BaseModel):
    """Space efficiency analysis."""
    total_built_area: float = Field(..., gt=0, description="Total built-up area in sq.ft")
    carpet_area: float = Field(..., gt=0, description="Carpet area in sq.ft")
    efficiency_ratio: float = Field(..., ge=0, le=1, description="Carpet to built-up area ratio")
    utilization_score: float = Field(..., ge=0, le=100, description="Space utilization score (0-100)")
    recommendations: List[str] = Field(default=[], description="Optimization recommendations")

class ArchitecturalDesign(BaseModel):
    """Complete architectural design output."""
    input_parameters: DesignInput
    far_recommendation: float = Field(..., gt=0, description="Recommended Floor Area Ratio")
    setbacks: Setbacks
    room_allocation: RoomAllocation
    structural_recommendations: StructuralRecommendations
    design_rationale: DesignRationale
    space_efficiency: SpaceEfficiency
    total_cost_estimate: Optional[float] = Field(None, description="Estimated construction cost")
    timeline_estimate: Optional[str] = Field(None, description="Estimated construction timeline")

class RoomDimensions(BaseModel):
    """Room dimensions for 2D layout."""
    length: float = Field(..., gt=0, description="Room length in feet")
    width: float = Field(..., gt=0, description="Room width in feet")
    x_position: float = Field(..., description="X position in layout")
    y_position: float = Field(..., description="Y position in layout")
    
    @root_validator(pre=True)
    def validate_positions(cls, values):
        """Handle floating-point precision issues for positions."""
        for field in ['x_position', 'y_position']:
            if field in values:
                val = values[field]
                # If the value is very close to zero but negative due to floating-point precision,
                # round it to zero
                if abs(val) < 1e-10 and val < 0:
                    values[field] = 0.0
                elif val < 0:
                    # For larger negative values, also set to 0 to ensure non-negative
                    values[field] = 0.0
                else:
                    # Ensure the value is properly rounded
                    values[field] = round(val, 6)
        return values

class DoorWindow(BaseModel):
    """Door and window specifications."""
    type: str = Field(..., description="Door or Window")
    width: float = Field(..., gt=0, description="Width in feet")
    height: float = Field(..., gt=0, description="Height in feet")
    x_position: float = Field(..., description="X position")
    y_position: float = Field(..., description="Y position")
    wall: str = Field(..., description="Which wall (North/South/East/West)")
    
    @root_validator(pre=True)
    def validate_positions(cls, values):
        """Handle floating-point precision issues for positions."""
        for field in ['x_position', 'y_position']:
            if field in values:
                val = values[field]
                # If the value is very close to zero but negative due to floating-point precision,
                # round it to zero
                if abs(val) < 1e-10 and val < 0:
                    values[field] = 0.0
                elif val < 0:
                    # For larger negative values, also set to 0 to ensure non-negative
                    values[field] = 0.0
                else:
                    # Ensure the value is properly rounded
                    values[field] = round(val, 6)
        return values

class FloorPlan(BaseModel):
    """2D floor plan data."""
    floor_number: int = Field(..., ge=0, description="Floor number (0 for ground)")
    rooms: Dict[str, RoomDimensions] = Field(..., description="Room dimensions and positions")
    doors_windows: List[DoorWindow] = Field(default=[], description="Door and window specifications")
    wall_thickness: float = Field(default=0.75, description="Wall thickness in feet (9 inches)")
    total_dimensions: Dict[str, float] = Field(..., description="Overall floor dimensions")

class VisualizationSpecs(BaseModel):
    """3D visualization specifications."""
    exterior_views: List[str] = Field(default=["front", "back", "left", "right"], description="Required exterior views")
    interior_rooms: List[str] = Field(..., description="Rooms to include in walkthrough")
    lighting_conditions: str = Field(..., description="Lighting based on orientation")
    material_palette: Dict[str, str] = Field(default={}, description="Material specifications")
    render_quality: str = Field(default="high", description="Render quality (low/medium/high)")
