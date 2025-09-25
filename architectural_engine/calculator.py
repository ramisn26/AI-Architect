"""
Architectural calculation engine for FAR, setbacks, and room allocations.
"""

import math
from typing import Dict, List, Tuple
from .schemas import (
    DesignInput, Setbacks, RoomAllocation, StructuralRecommendations,
    DesignRationale, SpaceEfficiency, FacingDirection, BuildingType
)

class ArchitecturalCalculator:
    """Core calculation engine for architectural design parameters."""
    
    # Standard room size recommendations (in sq.ft)
    ROOM_STANDARDS = {
        "living_room": {"min": 120, "optimal": 200, "max": 350},
        "master_bedroom": {"min": 120, "optimal": 150, "max": 200},
        "bedroom": {"min": 80, "optimal": 120, "max": 150},
        "kitchen": {"min": 60, "optimal": 100, "max": 150},
        "bathroom": {"min": 25, "optimal": 40, "max": 60},
        "balcony": {"min": 30, "optimal": 50, "max": 100},
        "corridor": {"min": 3, "optimal": 4, "max": 6},  # width in feet
        "staircase": {"min": 25, "optimal": 35, "max": 50},
        "parking": {"min": 120, "optimal": 150, "max": 200}
    }
    
    # FAR recommendations based on plot size and building type
    FAR_GUIDELINES = {
        BuildingType.INDEPENDENT_HOUSE: {
            "small": (0, 1000, 1.2),      # (min_size, max_size, far)
            "medium": (1000, 2500, 1.0),
            "large": (2500, 5000, 0.8),
            "very_large": (5000, float('inf'), 0.6)
        },
        BuildingType.DUPLEX: {
            "small": (0, 1200, 1.5),
            "medium": (1200, 3000, 1.2),
            "large": (3000, float('inf'), 1.0)
        },
        BuildingType.VILLA: {
            "small": (0, 2000, 0.8),
            "medium": (2000, 5000, 0.6),
            "large": (5000, float('inf'), 0.5)
        }
    }
    
    # Setback requirements based on plot size (in feet)
    SETBACK_GUIDELINES = {
        "small": (0, 1000, {"front": 5, "rear": 3, "sides": 3}),
        "medium": (1000, 2500, {"front": 8, "rear": 5, "sides": 5}),
        "large": (2500, 5000, {"front": 10, "rear": 8, "sides": 6}),
        "very_large": (5000, float('inf'), {"front": 15, "rear": 10, "sides": 8})
    }
    
    def __init__(self):
        self.vastu_principles = {
            FacingDirection.EAST: {
                "main_entrance": "East or Northeast",
                "kitchen": "Southeast",
                "master_bedroom": "Southwest",
                "pooja_room": "Northeast",
                "benefits": "Maximum morning sunlight, positive energy flow"
            },
            FacingDirection.WEST: {
                "main_entrance": "West or Northwest",
                "kitchen": "Southeast or Northwest",
                "master_bedroom": "Southwest",
                "pooja_room": "Northeast",
                "benefits": "Evening sunlight, good for commercial activities"
            },
            FacingDirection.NORTH: {
                "main_entrance": "North or Northeast",
                "kitchen": "Southeast",
                "master_bedroom": "Southwest",
                "pooja_room": "Northeast",
                "benefits": "Consistent natural light, wealth and prosperity"
            },
            FacingDirection.SOUTH: {
                "main_entrance": "South or Southeast",
                "kitchen": "Southeast",
                "master_bedroom": "Southwest",
                "pooja_room": "Northeast",
                "benefits": "Stable energy, good for long-term residence"
            }
        }
    
    def calculate_far(self, input_data: DesignInput) -> float:
        """Calculate recommended Floor Area Ratio."""
        land_size = input_data.land_size
        building_type = input_data.building_type
        
        if building_type not in self.FAR_GUIDELINES:
            building_type = BuildingType.INDEPENDENT_HOUSE
        
        guidelines = self.FAR_GUIDELINES[building_type]
        
        for category, (min_size, max_size, far) in guidelines.items():
            if min_size <= land_size < max_size:
                # Adjust FAR based on number of floors
                floor_multiplier = 1 + (input_data.floors - 1) * 0.3
                return min(far * floor_multiplier, 2.5)  # Cap at 2.5
        
        return 1.0  # Default FAR
    
    def calculate_setbacks(self, input_data: DesignInput) -> Setbacks:
        """Calculate required setbacks based on plot size and local norms."""
        land_size = input_data.land_size
        
        for category, (min_size, max_size, setbacks) in self.SETBACK_GUIDELINES.items():
            if min_size <= land_size < max_size:
                return Setbacks(
                    front=setbacks["front"],
                    rear=setbacks["rear"],
                    left=setbacks["sides"],
                    right=setbacks["sides"]
                )
        
        # Default setbacks for very large plots
        return Setbacks(front=15, rear=10, left=8, right=8)
    
    def calculate_room_allocation(self, input_data: DesignInput, available_area: float) -> RoomAllocation:
        """Calculate optimal room-wise area allocation."""
        bedrooms_count = int(input_data.bedroom_config[:-3])
        
        # Base allocation percentages
        allocation_percentages = {
            "living_room": 0.25,
            "kitchen": 0.12,
            "master_bedroom": 0.18,
            "other_bedrooms": 0.15 * (bedrooms_count - 1) if bedrooms_count > 1 else 0,
            "bathrooms": 0.08 * (bedrooms_count + 1),  # One common + one per bedroom
            "balcony": 0.08,
            "corridors": 0.10,
            "staircase": 0.04 if input_data.floors > 1 else 0,
            "utility": 0.03
        }
        
        # Adjust for single bedroom
        if bedrooms_count == 1:
            allocation_percentages["living_room"] = 0.30
            allocation_percentages["master_bedroom"] = 0.25
        
        # Calculate actual areas
        living_area = available_area * allocation_percentages["living_room"]
        kitchen_area = available_area * allocation_percentages["kitchen"]
        
        # Bedrooms
        bedrooms = {}
        if bedrooms_count >= 1:
            bedrooms["master_bedroom"] = available_area * allocation_percentages["master_bedroom"]
        
        for i in range(2, bedrooms_count + 1):
            bedroom_area = (available_area * allocation_percentages["other_bedrooms"]) / max(1, bedrooms_count - 1)
            bedrooms[f"bedroom_{i}"] = bedroom_area
        
        # Bathrooms
        bathrooms = {}
        total_bathroom_area = available_area * allocation_percentages["bathrooms"]
        bathroom_count = bedrooms_count + 1  # One common bathroom + one per bedroom for 2+ BHK
        
        if bedrooms_count == 1:
            bathrooms["bathroom_1"] = total_bathroom_area
        else:
            bathrooms["master_bathroom"] = total_bathroom_area * 0.4
            remaining_area = total_bathroom_area * 0.6
            for i in range(2, bathroom_count + 1):
                bathrooms[f"bathroom_{i}"] = remaining_area / max(1, bathroom_count - 1)
        
        return RoomAllocation(
            living_room=max(living_area, self.ROOM_STANDARDS["living_room"]["min"]),
            kitchen=max(kitchen_area, self.ROOM_STANDARDS["kitchen"]["min"]),
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            balcony=available_area * allocation_percentages["balcony"],
            corridors=available_area * allocation_percentages["corridors"],
            staircase=available_area * allocation_percentages["staircase"],
            parking=0,  # Calculated separately if needed
            utility=available_area * allocation_percentages["utility"]
        )
    
    def get_structural_recommendations(self, input_data: DesignInput) -> StructuralRecommendations:
        """Generate structural and circulation recommendations."""
        land_size = input_data.land_size
        floors = input_data.floors
        
        # Foundation type based on soil conditions and load
        if floors == 1 and land_size < 1500:
            foundation_type = "Strip Foundation with Plinth Beam"
        elif floors <= 2:
            foundation_type = "Isolated Footing with Tie Beams"
        else:
            foundation_type = "Mat Foundation or Pile Foundation"
        
        # Wall material recommendations
        if land_size < 1000:
            wall_material = "9-inch Brick Masonry with Plaster"
        else:
            wall_material = "9-inch Brick Masonry with Thermal Insulation"
        
        # Roofing system
        if floors == 1:
            roofing_system = "RCC Slab with Waterproofing"
        else:
            roofing_system = "RCC Slab with Thermal Insulation and Waterproofing"
        
        # Ventilation strategy based on orientation
        facing = input_data.facing
        if facing in [FacingDirection.EAST, FacingDirection.WEST]:
            ventilation_strategy = "Cross ventilation with East-West openings, avoid afternoon sun"
        else:
            ventilation_strategy = "North-South cross ventilation with clerestory windows"
        
        # Natural light optimization
        light_optimization = f"Maximize {facing.value.lower()} facing windows, use light wells for interior spaces"
        
        # Circulation flow
        circulation_flow = "Central corridor with direct access to all rooms, separate service and guest circulation"
        
        return StructuralRecommendations(
            foundation_type=foundation_type,
            wall_material=wall_material,
            roofing_system=roofing_system,
            ventilation_strategy=ventilation_strategy,
            natural_light_optimization=light_optimization,
            circulation_flow=circulation_flow
        )
    
    def generate_design_rationale(self, input_data: DesignInput) -> DesignRationale:
        """Generate comprehensive design rationale."""
        facing = input_data.facing
        vastu_info = self.vastu_principles.get(facing, self.vastu_principles[FacingDirection.EAST])
        
        orientation_benefits = vastu_info["benefits"]
        
        ventilation_strategy = f"""
        Optimized for {facing.value} orientation:
        - Main openings positioned to capture prevailing winds
        - Cross ventilation planned for maximum air circulation
        - Strategic placement of windows to avoid harsh sunlight
        - Natural light maximized during optimal hours
        """
        
        vastu_compliance = f"""
        Vastu principles applied:
        - Main entrance: {vastu_info['main_entrance']}
        - Kitchen placement: {vastu_info['kitchen']}
        - Master bedroom: {vastu_info['master_bedroom']}
        - Pooja room: {vastu_info['pooja_room']}
        - Water bodies and utilities positioned as per Vastu guidelines
        """
        
        zoning_compliance = """
        Design complies with:
        - Local building bylaws and setback requirements
        - Fire safety norms with adequate escape routes
        - Parking requirements as per local regulations
        - Height restrictions and FAR compliance
        - Accessibility guidelines for differently-abled
        """
        
        expansion_potential = f"""
        Future expansion possibilities:
        - Vertical expansion up to {3 - input_data.floors} additional floors
        - Horizontal expansion within setback limits
        - Provision for additional parking spaces
        - Infrastructure ready for solar panels and rainwater harvesting
        """
        
        sustainability_features = [
            "Rainwater harvesting system",
            "Solar panel ready rooftop",
            "Natural ventilation to reduce AC load",
            "LED lighting provisions",
            "Waste segregation and composting area",
            "Native landscaping for low maintenance"
        ]
        
        return DesignRationale(
            orientation_benefits=orientation_benefits,
            ventilation_strategy=ventilation_strategy.strip(),
            vastu_compliance=vastu_compliance.strip(),
            zoning_compliance=zoning_compliance.strip(),
            expansion_potential=expansion_potential.strip(),
            sustainability_features=sustainability_features
        )
    
    def calculate_space_efficiency(self, input_data: DesignInput, room_allocation: RoomAllocation, 
                                 total_built_area: float) -> SpaceEfficiency:
        """Calculate space efficiency metrics."""
        
        # Calculate carpet area (usable area)
        carpet_area = (
            room_allocation.living_room +
            sum(room_allocation.bedrooms.values()) +
            room_allocation.kitchen +
            room_allocation.balcony +
            room_allocation.utility
        )
        
        # Efficiency ratio (carpet area to built-up area)
        efficiency_ratio = carpet_area / total_built_area if total_built_area > 0 else 0
        
        # Utilization score based on multiple factors
        utilization_score = self._calculate_utilization_score(
            input_data, room_allocation, efficiency_ratio
        )
        
        # Generate recommendations
        recommendations = self._generate_efficiency_recommendations(
            efficiency_ratio, utilization_score, room_allocation
        )
        
        return SpaceEfficiency(
            total_built_area=total_built_area,
            carpet_area=carpet_area,
            efficiency_ratio=efficiency_ratio,
            utilization_score=utilization_score,
            recommendations=recommendations
        )
    
    def _calculate_utilization_score(self, input_data: DesignInput, 
                                   room_allocation: RoomAllocation, efficiency_ratio: float) -> float:
        """Calculate overall space utilization score."""
        score = 0
        
        # Efficiency ratio score (40% weightage)
        if efficiency_ratio >= 0.75:
            score += 40
        elif efficiency_ratio >= 0.65:
            score += 30
        elif efficiency_ratio >= 0.55:
            score += 20
        else:
            score += 10
        
        # Room size optimization score (30% weightage)
        room_score = 0
        total_rooms = len(room_allocation.bedrooms) + 1  # +1 for living room
        
        # Check living room size
        living_std = self.ROOM_STANDARDS["living_room"]
        if living_std["min"] <= room_allocation.living_room <= living_std["max"]:
            room_score += 10
        
        # Check bedroom sizes
        for bedroom, area in room_allocation.bedrooms.items():
            if "master" in bedroom.lower():
                std = self.ROOM_STANDARDS["master_bedroom"]
            else:
                std = self.ROOM_STANDARDS["bedroom"]
            
            if std["min"] <= area <= std["max"]:
                room_score += 10 / len(room_allocation.bedrooms)
        
        # Check kitchen size
        kitchen_std = self.ROOM_STANDARDS["kitchen"]
        if kitchen_std["min"] <= room_allocation.kitchen <= kitchen_std["max"]:
            room_score += 10
        
        score += min(room_score, 30)
        
        # Circulation efficiency score (20% weightage)
        total_area = sum(room_allocation.bedrooms.values()) + room_allocation.living_room + room_allocation.kitchen
        circulation_ratio = room_allocation.corridors / total_area if total_area > 0 else 0
        
        if 0.08 <= circulation_ratio <= 0.15:  # Optimal circulation ratio
            score += 20
        elif 0.05 <= circulation_ratio <= 0.20:
            score += 15
        else:
            score += 5
        
        # Balance score (10% weightage)
        bedrooms_count = int(input_data.bedroom_config[:-3])
        if bedrooms_count > 1:
            bedroom_areas = list(room_allocation.bedrooms.values())
            if len(bedroom_areas) > 1:
                area_variance = max(bedroom_areas) - min(bedroom_areas)
                if area_variance <= 30:  # Well balanced bedroom sizes
                    score += 10
                elif area_variance <= 50:
                    score += 7
                else:
                    score += 3
        else:
            score += 10  # Single bedroom gets full balance score
        
        return min(score, 100)
    
    def _generate_efficiency_recommendations(self, efficiency_ratio: float, 
                                           utilization_score: float, 
                                           room_allocation: RoomAllocation) -> List[str]:
        """Generate recommendations for improving space efficiency."""
        recommendations = []
        
        if efficiency_ratio < 0.60:
            recommendations.append("Consider reducing corridor width to increase usable area")
            recommendations.append("Optimize wall thickness and structural elements")
        
        if utilization_score < 70:
            recommendations.append("Review room sizes against functional requirements")
            recommendations.append("Consider multi-functional spaces to improve efficiency")
        
        # Check for oversized rooms
        living_std = self.ROOM_STANDARDS["living_room"]
        if room_allocation.living_room > living_std["max"]:
            recommendations.append("Living room is oversized - consider creating a separate dining area")
        
        kitchen_std = self.ROOM_STANDARDS["kitchen"]
        if room_allocation.kitchen > kitchen_std["max"]:
            recommendations.append("Kitchen is oversized - consider adding utility area or breakfast counter")
        
        # Check for undersized rooms
        if room_allocation.living_room < living_std["min"]:
            recommendations.append("Living room is undersized - consider expanding or combining with dining")
        
        if room_allocation.kitchen < kitchen_std["min"]:
            recommendations.append("Kitchen is undersized - consider L-shaped or parallel layout")
        
        # Circulation recommendations
        total_area = sum(room_allocation.bedrooms.values()) + room_allocation.living_room + room_allocation.kitchen
        circulation_ratio = room_allocation.corridors / total_area if total_area > 0 else 0
        
        if circulation_ratio > 0.20:
            recommendations.append("Excessive circulation space - consider open plan layout")
        elif circulation_ratio < 0.05:
            recommendations.append("Insufficient circulation space - ensure adequate passage width")
        
        if not recommendations:
            recommendations.append("Space utilization is optimal for the given requirements")
        
        return recommendations
