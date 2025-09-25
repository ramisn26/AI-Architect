"""
2D floor plan layout generator with CAD-style output capabilities.
"""

import math
from typing import Dict, List, Tuple, Optional
from .schemas import (
    ArchitecturalDesign, FloorPlan, RoomDimensions, DoorWindow,
    FacingDirection, StaircaseType
)

class FloorPlanGenerator:
    """Generates 2D floor plan layouts from architectural designs."""
    
    def __init__(self):
        self.wall_thickness = 0.75  # 9 inches in feet
        self.door_width = 3.0  # Standard door width
        self.window_width = 4.0  # Standard window width
        self.corridor_width = 4.0  # Standard corridor width
    
    def _safe_position(self, value: float) -> float:
        """Ensure position values are properly rounded to avoid floating-point precision issues."""
        # Round to 6 decimal places to avoid tiny negative numbers
        rounded = round(value, 6)
        # If the rounded value is very close to zero but negative, make it zero
        if abs(rounded) < 1e-10 and rounded < 0:
            return 0.0
        return max(0.0, rounded)  # Ensure non-negative
    
    def generate_layout(self, design: ArchitecturalDesign, floor_number: int = 0) -> FloorPlan:
        """Generate 2D floor plan layout for specific floor."""
        return self._generate_floor_specific_layout(design, floor_number)
    
    def generate_all_floors(self, design: ArchitecturalDesign) -> List[FloorPlan]:
        """Generate floor plans for all floors in the building."""
        floor_plans = []
        total_floors = design.input_parameters.floors
        
        for floor_num in range(total_floors):
            floor_plan = self._generate_floor_specific_layout(design, floor_num)
            floor_plans.append(floor_plan)
        
        return floor_plans
    
    def _generate_floor_specific_layout(self, design: ArchitecturalDesign, floor_number: int = 0) -> FloorPlan:
        """Generate 2D floor plan layout."""
        # Calculate available building dimensions
        setbacks = design.setbacks
        land_side = design.input_parameters.land_size ** 0.5
        
        building_length = land_side - setbacks.front - setbacks.rear
        building_width = land_side - setbacks.left - setbacks.right
        
        # Generate room layout
        rooms = self._generate_room_layout(
            design.room_allocation,
            building_length,
            building_width,
            design.input_parameters.facing,
            design.input_parameters.staircase_type,
            floor_number
        )
        
        # Generate doors and windows
        doors_windows = self._generate_doors_windows(
            rooms,
            design.input_parameters.facing,
            building_length,
            building_width
        )
        
        return FloorPlan(
            floor_number=floor_number,
            rooms=rooms,
            doors_windows=doors_windows,
            wall_thickness=self.wall_thickness,
            total_dimensions={
                "length": building_length,
                "width": building_width,
                "total_area": building_length * building_width
            }
        )
    
    def _generate_room_layout(self, room_allocation, building_length: float, 
                            building_width: float, facing: FacingDirection,
                            staircase_type: Optional[StaircaseType], 
                            floor_number: int) -> Dict[str, RoomDimensions]:
        """Generate optimal room layout based on Vastu and functional requirements."""
        
        # Get floor-specific room allocation
        floor_rooms = self._get_floor_specific_rooms(room_allocation, floor_number)
        
        # Calculate room dimensions from areas
        room_dims = self._calculate_room_dimensions(floor_rooms, building_length, building_width)
        
        # Position rooms based on facing direction and floor
        if facing == FacingDirection.EAST:
            rooms = self._layout_east_facing(room_dims, building_length, building_width, floor_number)
        elif facing == FacingDirection.WEST:
            rooms = self._layout_west_facing(room_dims, building_length, building_width, floor_number)
        elif facing == FacingDirection.NORTH:
            rooms = self._layout_north_facing(room_dims, building_length, building_width, floor_number)
        else:  # South facing
            rooms = self._layout_south_facing(room_dims, building_length, building_width, floor_number)
        
        return rooms
    
    def _get_floor_specific_rooms(self, room_allocation, floor_number: int) -> Dict[str, float]:
        """Distribute rooms across floors based on architectural best practices."""
        
        if floor_number == 0:  # Ground Floor
            # Ground floor typically has: Living room, Kitchen, Dining, Guest bedroom, Common bathroom, Parking
            ground_floor_rooms = {
                'living_room': room_allocation.living_room,
                'kitchen': room_allocation.kitchen,
                'dining_room': room_allocation.living_room * 0.6,  # Dining area
                'guest_bedroom': list(room_allocation.bedrooms.values())[0] if room_allocation.bedrooms else 0,
                'guest_bathroom': list(room_allocation.bathrooms.values())[0] if room_allocation.bathrooms else 0,
                'corridors': room_allocation.corridors * 0.6,
                'parking': room_allocation.parking,
                'utility': room_allocation.utility,
                'pooja_room': room_allocation.pooja_room
            }
            
            # Add staircase if multi-floor
            if hasattr(room_allocation, 'staircase') and room_allocation.staircase > 0:
                ground_floor_rooms['staircase'] = room_allocation.staircase
                
            return ground_floor_rooms
            
        else:  # Upper Floors (1st, 2nd, etc.)
            # Upper floors typically have: Bedrooms, Bathrooms, Family room, Balcony
            upper_floor_rooms = {}
            
            # Distribute bedrooms across upper floors
            bedrooms = list(room_allocation.bedrooms.items())
            bathrooms = list(room_allocation.bathrooms.items())
            
            # For first floor
            if floor_number == 1:
                # Master bedroom and additional bedrooms
                if len(bedrooms) > 1:
                    upper_floor_rooms['master_bedroom'] = bedrooms[1][1]  # Second bedroom becomes master
                if len(bedrooms) > 2:
                    upper_floor_rooms['bedroom_2'] = bedrooms[2][1]
                
                # Master bathroom and additional bathrooms
                if len(bathrooms) > 1:
                    upper_floor_rooms['master_bathroom'] = bathrooms[1][1]
                if len(bathrooms) > 2:
                    upper_floor_rooms['bathroom_2'] = bathrooms[2][1]
                
                # Family/Living area on first floor
                upper_floor_rooms['family_room'] = room_allocation.living_room * 0.7
                upper_floor_rooms['balcony'] = room_allocation.balcony
                upper_floor_rooms['corridors'] = room_allocation.corridors * 0.4
                
                # Add staircase if more floors above
                if hasattr(room_allocation, 'staircase') and room_allocation.staircase > 0:
                    upper_floor_rooms['staircase'] = room_allocation.staircase * 0.8
            
            # For second floor and above
            elif floor_number >= 2:
                remaining_bedrooms = bedrooms[3:] if len(bedrooms) > 3 else []
                remaining_bathrooms = bathrooms[3:] if len(bathrooms) > 3 else []
                
                for i, (bed_name, bed_area) in enumerate(remaining_bedrooms):
                    upper_floor_rooms[f'bedroom_{i+3}'] = bed_area
                
                for i, (bath_name, bath_area) in enumerate(remaining_bathrooms):
                    upper_floor_rooms[f'bathroom_{i+3}'] = bath_area
                
                # Study room or additional spaces
                upper_floor_rooms['study_room'] = room_allocation.living_room * 0.5
                upper_floor_rooms['storage'] = room_allocation.utility * 0.5
                upper_floor_rooms['corridors'] = room_allocation.corridors * 0.3
            
            return upper_floor_rooms
        
        # Add staircase if multi-floor
        if floor_number == 0 and staircase_type and room_allocation.staircase > 0:
            stair_dims = self._calculate_staircase_dimensions(room_allocation.staircase, staircase_type)
            rooms["staircase"] = self._position_staircase(stair_dims, rooms, building_length, building_width)
        
        return rooms
    
    def _calculate_room_dimensions(self, room_allocation, building_length: float, 
                                 building_width: float) -> Dict[str, Tuple[float, float]]:
        """Calculate optimal dimensions for each room based on area allocation."""
        
        room_dims = {}
        
        # Handle both dictionary and object inputs
        if isinstance(room_allocation, dict):
            # Dictionary input from floor-specific rooms
            for room_name, area in room_allocation.items():
                if area > 0:  # Only process rooms with positive area
                    if 'living' in room_name.lower() or 'family' in room_name.lower():
                        # Living/family rooms - rectangular
                        length = min(math.sqrt(area * 1.5), building_length * 0.6)
                        width = area / length
                    elif 'kitchen' in room_name.lower():
                        # Kitchen - compact rectangular
                        length = min(math.sqrt(area * 1.2), building_width * 0.4)
                        width = area / length
                    elif 'bedroom' in room_name.lower() or 'master' in room_name.lower():
                        # Bedrooms - square to rectangular
                        if 'master' in room_name.lower():
                            length = math.sqrt(area * 1.1)
                        else:
                            length = math.sqrt(area * 1.0)
                        width = area / length
                    elif 'bathroom' in room_name.lower():
                        # Bathrooms - compact square
                        length = math.sqrt(area * 0.8)
                        width = area / length
                    elif 'dining' in room_name.lower():
                        # Dining room - rectangular
                        length = math.sqrt(area * 1.3)
                        width = area / length
                    elif 'staircase' in room_name.lower():
                        # Staircase - narrow rectangular
                        length = math.sqrt(area * 2.0)
                        width = area / length
                    else:
                        # Default - square
                        length = math.sqrt(area)
                        width = area / length
                    
                    # Ensure minimum dimensions
                    length = max(length, 6.0)  # Minimum 6 feet
                    width = max(width, 4.0)    # Minimum 4 feet
                    
                    room_dims[room_name] = (length, width)
            
            return room_dims
        
        # Original object-based logic for backward compatibility
        # Living room - typically rectangular
        living_area = room_allocation.living_room
        living_length = min(math.sqrt(living_area * 1.5), building_length * 0.6)
        living_width = living_area / living_length
        room_dims["living_room"] = (living_length, living_width)
        
        # Kitchen
        kitchen_area = room_allocation.kitchen
        kitchen_length = min(math.sqrt(kitchen_area * 1.2), building_width * 0.4)
        kitchen_width = kitchen_area / kitchen_length
        room_dims["kitchen"] = (kitchen_length, kitchen_width)
        
        # Bedrooms
        for bedroom_name, area in room_allocation.bedrooms.items():
            if "master" in bedroom_name.lower():
                length = math.sqrt(area * 1.1)
                width = area / length
            else:
                length = math.sqrt(area * 1.2)
                width = area / length
            room_dims[bedroom_name] = (length, width)
        
        # Bathrooms
        for bathroom_name, area in room_allocation.bathrooms.items():
            length = math.sqrt(area * 1.5)
            width = area / length
            room_dims[bathroom_name] = (length, width)
        
        # Balcony
        if room_allocation.balcony > 0:
            balcony_length = min(building_length * 0.8, 20)
            balcony_width = room_allocation.balcony / balcony_length
            room_dims["balcony"] = (balcony_length, balcony_width)
        
        # Utility room
        if room_allocation.utility > 0:
            utility_length = math.sqrt(room_allocation.utility)
            utility_width = room_allocation.utility / utility_length
            room_dims["utility"] = (utility_length, utility_width)
        
        return room_dims
    
    def _layout_east_facing(self, room_dims: Dict[str, Tuple[float, float]], 
                          building_length: float, building_width: float, floor_number: int = 0) -> Dict[str, RoomDimensions]:
        """Layout rooms for East-facing building following professional architectural principles."""
        
        rooms = {}
        current_x = 0
        current_y = 0
        
        # Ground floor layout (similar to uploaded blueprint)
        if floor_number == 0:
            # Left side - Living areas
            if "living_room" in room_dims:
                length, width = room_dims["living_room"]
                rooms["living_room"] = RoomDimensions(
                    length=length, width=width, 
                    x_position=self._safe_position(current_x), 
                    y_position=self._safe_position(current_y)
                )
                current_y += width
            
            # Dining area adjacent to living room
            if "dining_room" in room_dims:
                length, width = room_dims["dining_room"]
                rooms["dining_room"] = RoomDimensions(
                    length=length, width=width, 
                    x_position=self._safe_position(current_x), 
                    y_position=self._safe_position(current_y)
                )
                current_y += width
            
            # Pooja room in northeast corner (Vastu compliant)
            if "pooja_room" in room_dims:
                length, width = room_dims["pooja_room"]
                rooms["pooja_room"] = RoomDimensions(
                    length=length, width=width, 
                    x_position=self._safe_position(current_x), 
                    y_position=self._safe_position(building_width - width)
                )
            
            # Right side - Service areas and bedrooms
            right_x = building_length * 0.6
            right_y = 0
            
            # Kitchen in southeast (Vastu compliant)
            if "kitchen" in room_dims:
                length, width = room_dims["kitchen"]
                rooms["kitchen"] = RoomDimensions(
                    length=length, width=width, 
                    x_position=building_length - length, y_position=right_y
                )
                right_y += width
            
            # Utility room adjacent to kitchen
            if "utility" in room_dims:
                length, width = room_dims["utility"]
                rooms["utility"] = RoomDimensions(
                    length=length, width=width,
                    x_position=building_length - length, y_position=right_y
                )
                right_y += width
            
            # Guest bedroom
            if "guest_bedroom" in room_dims:
                length, width = room_dims["guest_bedroom"]
                rooms["guest_bedroom"] = RoomDimensions(
                    length=length, width=width,
                    x_position=right_x, y_position=right_y
                )
                right_y += width
            
            # Bathrooms positioned centrally for accessibility
            bathroom_x = building_length * 0.45
            bathroom_y = building_width * 0.3
            for name, (length, width) in room_dims.items():
                if "bathroom" in name.lower():
                    rooms[name] = RoomDimensions(
                        length=length, width=width,
                        x_position=bathroom_x, y_position=bathroom_y
                    )
                    bathroom_y += width + 1  # Space between bathrooms
            
            # Staircase in central location
            if "staircase" in room_dims:
                length, width = room_dims["staircase"]
                rooms["staircase"] = RoomDimensions(
                    length=length, width=width,
                    x_position=building_length * 0.35, y_position=building_width * 0.5
                )
            
            # Parking at the front or side
            if "parking" in room_dims:
                length, width = room_dims["parking"]
                rooms["parking"] = RoomDimensions(
                    length=length, width=width,
                    x_position=0, y_position=building_width * 0.7
                )
        
        # Upper floor layout
        else:
            # Master bedroom in southwest (Vastu compliant)
            if "master_bedroom" in room_dims:
                length, width = room_dims["master_bedroom"]
                rooms["master_bedroom"] = RoomDimensions(
                    length=length, width=width,
                    x_position=building_length - length, 
                    y_position=building_width - width
                )
            
            # Other bedrooms
            bedroom_x = 0
            bedroom_y = 0
            for name, (length, width) in room_dims.items():
                if "bedroom" in name.lower() and "master" not in name.lower():
                    rooms[name] = RoomDimensions(
                        length=length, width=width,
                        x_position=bedroom_x, y_position=bedroom_y
                    )
                    bedroom_y += width + 1  # Space between rooms
            
            # Family room/living area
            if "family_room" in room_dims:
                length, width = room_dims["family_room"]
                rooms["family_room"] = RoomDimensions(
                    length=length, width=width,
                    x_position=building_length * 0.3, y_position=0
                )
            
            # Balcony in north or east (good ventilation)
            if "balcony" in room_dims:
                length, width = room_dims["balcony"]
                rooms["balcony"] = RoomDimensions(
                    length=length, width=width,
                    x_position=0, y_position=building_width - width
                )
            
            # Bathrooms
            bathroom_x = building_length * 0.6
            bathroom_y = building_width * 0.3
            for name, (length, width) in room_dims.items():
                if "bathroom" in name.lower():
                    rooms[name] = RoomDimensions(
                        length=length, width=width,
                        x_position=bathroom_x, y_position=bathroom_y
                    )
                    bathroom_y += width + 1
            
            # Staircase continuation
            if "staircase" in room_dims:
                length, width = room_dims["staircase"]
                rooms["staircase"] = RoomDimensions(
                    length=length, width=width,
                    x_position=building_length * 0.35, y_position=building_width * 0.5
                )
        
        return rooms
    
    def _layout_west_facing(self, room_dims: Dict[str, Tuple[float, float]], 
                          building_length: float, building_width: float, floor_number: int = 0) -> Dict[str, RoomDimensions]:
        """Layout rooms for West-facing building."""
        # Mirror the east-facing layout
        east_layout = self._layout_east_facing(room_dims, building_length, building_width)
        return {name: RoomDimensions(
            length=room.length, width=room.width,
            x_position=building_length - room.x_position - room.length,
            y_position=room.y_position
        ) for name, room in east_layout.items()}
    
    def _layout_north_facing(self, room_dims: Dict[str, Tuple[float, float]], 
                           building_length: float, building_width: float, floor_number: int = 0) -> Dict[str, RoomDimensions]:
        """Layout rooms for North-facing building."""
        # Rotate the east-facing layout
        east_layout = self._layout_east_facing(room_dims, building_width, building_length)
        return {name: RoomDimensions(
            length=room.width, width=room.length,
            x_position=room.y_position,
            y_position=building_width - room.x_position - room.width
        ) for name, room in east_layout.items()}
    
    def _layout_south_facing(self, room_dims: Dict[str, Tuple[float, float]], 
                           building_length: float, building_width: float, floor_number: int = 0) -> Dict[str, RoomDimensions]:
        """Layout rooms for South-facing building."""
        # Mirror the north-facing layout
        north_layout = self._layout_north_facing(room_dims, building_length, building_width)
        return {name: RoomDimensions(
            length=room.length, width=room.width,
            x_position=room.x_position,
            y_position=building_width - room.y_position - room.width
        ) for name, room in north_layout.items()}
    
    def _calculate_staircase_dimensions(self, area: float, staircase_type: StaircaseType) -> Tuple[float, float]:
        """Calculate staircase dimensions based on type and area."""
        if staircase_type == StaircaseType.STRAIGHT:
            width = 4.0
            length = area / width
        elif staircase_type == StaircaseType.L_SHAPED:
            side = math.sqrt(area)
            length = width = side
        elif staircase_type == StaircaseType.U_SHAPED:
            width = 6.0
            length = area / width
        else:  # Spiral or Winder
            radius = math.sqrt(area / math.pi)
            length = width = radius * 2
        
        return (length, width)
    
    def _position_staircase(self, stair_dims: Tuple[float, float], 
                          rooms: Dict[str, RoomDimensions],
                          building_length: float, building_width: float) -> RoomDimensions:
        """Position staircase optimally within the layout."""
        length, width = stair_dims
        
        # Position in central location
        x_position = building_length * 0.4
        y_position = building_width * 0.4
        
        return RoomDimensions(
            length=length, width=width, x_position=x_position, y_position=y_position
        )
    
    def _generate_doors_windows(self, rooms: Dict[str, RoomDimensions], 
                              facing: FacingDirection, building_length: float,
                              building_width: float) -> List[DoorWindow]:
        """Generate door and window positions."""
        doors_windows = []
        
        # Main entrance door
        if facing == FacingDirection.EAST:
            doors_windows.append(DoorWindow(
                type="Door", width=3.0, height=7.0,
                x_position=building_length * 0.1, y_position=0, wall="East"
            ))
        
        # Windows for each room
        for room_name, room in rooms.items():
            if room_name in ["living_room", "master_bedroom"]:
                # Large windows
                doors_windows.append(DoorWindow(
                    type="Window", width=4.0, height=4.0,
                    x_position=room.x_position + room.length/2,
                    y_position=room.y_position, wall="Front"
                ))
            elif "bedroom" in room_name:
                # Medium windows
                doors_windows.append(DoorWindow(
                    type="Window", width=3.0, height=3.5,
                    x_position=room.x_position + room.length/2,
                    y_position=room.y_position, wall="Front"
                ))
            elif room_name == "kitchen":
                # Kitchen window
                doors_windows.append(DoorWindow(
                    type="Window", width=2.5, height=3.0,
                    x_position=room.x_position + room.length/2,
                    y_position=room.y_position, wall="Side"
                ))
        
        return doors_windows
