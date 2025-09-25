"""
Main architectural designer class that orchestrates the design generation process.
"""

from typing import Dict, Any, Optional, List
import json
from .schemas import DesignInput, ArchitecturalDesign, FloorPlan
from .calculator import ArchitecturalCalculator
from .validator import DesignValidator

class ArchitecturalDesigner:
    """Main class for generating comprehensive architectural designs."""
    
    def __init__(self):
        self.calculator = ArchitecturalCalculator()
        self.validator = DesignValidator()
        # Initialize layout generator
        from .layout_generator import FloorPlanGenerator
        self.layout_generator = FloorPlanGenerator()
    
    def generate_design(self, input_data: Dict[str, Any]) -> ArchitecturalDesign:
        """
        Generate a complete architectural design from input parameters.
        
        Args:
            input_data: Dictionary containing design input parameters
            
        Returns:
            ArchitecturalDesign: Complete design with all calculations and recommendations
        """
        # Validate and parse input
        design_input = DesignInput(**input_data)
        
        # Validate design feasibility
        validation_result = self.validator.validate_design_feasibility(design_input)
        if not validation_result.is_valid:
            raise ValueError(f"Design validation failed: {validation_result.errors}")
        
        # Calculate FAR and available area
        far = self.calculator.calculate_far(design_input)
        setbacks = self.calculator.calculate_setbacks(design_input)
        
        # Calculate buildable area
        buildable_length = (design_input.land_size ** 0.5) - setbacks.front - setbacks.rear
        buildable_width = (design_input.land_size ** 0.5) - setbacks.left - setbacks.right
        buildable_area = buildable_length * buildable_width
        
        # Calculate total built area based on FAR
        total_built_area = min(design_input.land_size * far, buildable_area * design_input.floors)
        available_area_per_floor = total_built_area / design_input.floors
        
        # Generate room allocation
        room_allocation = self.calculator.calculate_room_allocation(design_input, available_area_per_floor)
        
        # Get structural recommendations
        structural_recommendations = self.calculator.get_structural_recommendations(design_input)
        
        # Generate design rationale
        design_rationale = self.calculator.generate_design_rationale(design_input)
        
        # Calculate space efficiency
        space_efficiency = self.calculator.calculate_space_efficiency(
            design_input, room_allocation, total_built_area
        )
        
        # Estimate cost and timeline
        cost_estimate = self._estimate_construction_cost(total_built_area, design_input.building_type)
        timeline_estimate = self._estimate_construction_timeline(total_built_area, design_input.floors)
        
        return ArchitecturalDesign(
            input_parameters=design_input,
            far_recommendation=far,
            setbacks=setbacks,
            room_allocation=room_allocation,
            structural_recommendations=structural_recommendations,
            design_rationale=design_rationale,
            space_efficiency=space_efficiency,
            total_cost_estimate=cost_estimate,
            timeline_estimate=timeline_estimate
        )
    
    def generate_floor_plan(self, design: ArchitecturalDesign, floor_number: int = 0) -> FloorPlan:
        """
        Generate 2D floor plan layout from architectural design.
        
        Args:
            design: Complete architectural design
            floor_number: Floor number (0 for ground floor)
            
        Returns:
            FloorPlan: 2D layout with room positions and dimensions
        """
        return self.layout_generator.generate_layout(design, floor_number)
    
    def generate_all_floor_plans(self, design: ArchitecturalDesign) -> List[FloorPlan]:
        """
        Generate floor plans for all floors in the building.
        
        Args:
            design: Complete architectural design
            
        Returns:
            List[FloorPlan]: Floor plans for all floors
        """
        return self.layout_generator.generate_all_floors(design)
    
    def _create_basic_floor_plan(self, design: ArchitecturalDesign, floor_number: int = 0) -> FloorPlan:
        """Create a basic floor plan when layout generator is not available."""
        from .schemas import FloorPlan, RoomDimensions, DoorWindow
        
        # Calculate building dimensions
        setbacks = design.setbacks
        land_side = design.input_parameters.land_size ** 0.5
        building_length = land_side - setbacks.front - setbacks.rear
        building_width = land_side - setbacks.left - setbacks.right
        
        # Create basic room layout
        rooms = {}
        current_x = 0
        current_y = 0
        
        # Living room
        living_area = design.room_allocation.living_room
        living_length = min((living_area / 12) ** 0.5 * 1.5, building_length * 0.6)
        living_width = living_area / living_length
        rooms["living_room"] = RoomDimensions(
            length=living_length, width=living_width, 
            x_position=current_x, y_position=current_y
        )
        current_y += living_width
        
        # Kitchen
        kitchen_area = design.room_allocation.kitchen
        kitchen_length = min((kitchen_area / 8) ** 0.5 * 1.2, building_width * 0.4)
        kitchen_width = kitchen_area / kitchen_length
        rooms["kitchen"] = RoomDimensions(
            length=kitchen_length, width=kitchen_width,
            x_position=building_length - kitchen_length, y_position=0
        )
        
        # Bedrooms
        bedroom_x = building_length * 0.5
        bedroom_y = current_y
        for bedroom_name, area in design.room_allocation.bedrooms.items():
            bedroom_length = (area / 10) ** 0.5 * 1.2
            bedroom_width = area / bedroom_length
            rooms[bedroom_name] = RoomDimensions(
                length=bedroom_length, width=bedroom_width,
                x_position=bedroom_x, y_position=bedroom_y
            )
            bedroom_y += bedroom_width
        
        # Basic doors and windows
        doors_windows = [
            DoorWindow(
                type="Door", width=3.0, height=7.0,
                x_position=building_length * 0.1, y_position=0, wall="Front"
            )
        ]
        
        return FloorPlan(
            floor_number=floor_number,
            rooms=rooms,
            doors_windows=doors_windows,
            wall_thickness=0.75,
            total_dimensions={
                "length": building_length,
                "width": building_width,
                "total_area": building_length * building_width
            }
        )
    
    def export_design_json(self, design: ArchitecturalDesign, filepath: str) -> None:
        """Export design to JSON file."""
        design_dict = design.dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(design_dict, f, indent=2, ensure_ascii=False)
    
    def load_design_json(self, filepath: str) -> ArchitecturalDesign:
        """Load design from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            design_dict = json.load(f)
        return ArchitecturalDesign(**design_dict)
    
    def _estimate_construction_cost(self, built_area: float, building_type: str) -> float:
        """Estimate construction cost based on area and building type."""
        # Cost per sq.ft in INR (approximate rates for 2024)
        cost_rates = {
            "Independent House": 1800,  # Basic construction
            "Duplex": 2000,
            "Villa": 2500,
            "Row House": 1600,
            "Apartment": 1400
        }
        
        base_rate = cost_rates.get(building_type, 1800)
        
        # Add cost variations based on area (economies/diseconomies of scale)
        if built_area < 800:
            multiplier = 1.2  # Higher cost per sq.ft for smaller areas
        elif built_area > 2500:
            multiplier = 0.9  # Lower cost per sq.ft for larger areas
        else:
            multiplier = 1.0
        
        return built_area * base_rate * multiplier
    
    def _estimate_construction_timeline(self, built_area: float, floors: int) -> str:
        """Estimate construction timeline."""
        # Base timeline calculation
        base_months = 6  # Minimum timeline
        area_months = built_area / 200  # 1 month per 200 sq.ft
        floor_months = (floors - 1) * 2  # Additional 2 months per extra floor
        
        total_months = base_months + area_months + floor_months
        
        if total_months <= 8:
            return f"{int(total_months)} months"
        elif total_months <= 12:
            return f"{int(total_months)} months (including finishing)"
        else:
            years = int(total_months // 12)
            months = int(total_months % 12)
            if months == 0:
                return f"{years} year{'s' if years > 1 else ''}"
            else:
                return f"{years} year{'s' if years > 1 else ''} {months} months"
