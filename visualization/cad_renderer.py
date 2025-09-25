"""
Professional Architect's Blueprint Renderer for architectural designs.
Creates industry-ready, certified architect-quality floor plans with comprehensive
dimensions, professional symbols, and detailed architectural elements.

Features:
- Professional architectural symbols (stairs, doors, windows)
- Comprehensive dimension system with extension lines
- Industry-standard title blocks and compass rose
- Proper wall thickness representation
- Room labeling with areas and dimensions
- Balcony and utility room representations
"""

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Arrow, FancyArrowPatch
import numpy as np
from typing import Dict, List, Tuple, Optional
import io
import base64
import math

import sys
from pathlib import Path

# Add parent directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from architectural_engine.schemas import FloorPlan, RoomDimensions, DoorWindow

class CADRenderer:
    """Renders professional architect-quality 2D floor plans with proper dimensions and labels."""
    
    def __init__(self):
        # Professional Blueprint styling parameters
        self.wall_color = '#000000'  # Black walls for professional look
        self.wall_linewidth = 3.0  # Thicker walls for better visibility
        self.interior_wall_linewidth = 2.0  # Interior walls slightly thinner
        self.room_fill_color = '#FFFFFF'  # White interior
        self.room_edge_color = '#000000'
        self.dimension_color = '#FF0000'  # Red dimensions (standard)
        self.dimension_line_color = '#000000'
        self.text_color = '#000000'
        self.grid_color = '#E8E8E8'  # Professional grid color
        self.door_color = '#8B4513'  # Brown doors
        self.window_color = '#4169E1'  # Blue windows
        self.title_box_color = '#F0F8FF'
        self.stair_color = '#696969'  # Gray for stairs
        self.balcony_color = '#F5F5DC'  # Beige for balconies
        self.utility_color = '#E6E6FA'  # Lavender for utility areas
        
        # Professional font settings
        self.title_fontsize = 16
        self.subtitle_fontsize = 14
        self.label_fontsize = 11
        self.dimension_fontsize = 9
        self.room_label_fontsize = 10
        self.area_fontsize = 9
        
        # Dimension settings
        self.dimension_offset = 3.0  # Distance from walls
        self.dimension_extension = 2.0  # Extension line length
        self.arrow_size = 0.5
        self.wall_thickness = 0.75  # Standard 9-inch wall thickness
        
        # Professional architectural standards
        self.door_swing_radius = 3.0  # Standard door swing
        self.window_sill_height = 3.0  # Standard window sill
        self.stair_tread_depth = 1.0  # Standard stair tread
        self.stair_riser_height = 0.75  # Standard stair riser
        
    def render_floor_plan(self, floor_plan: FloorPlan, title: str = "Architectural Floor Plan", 
                         show_dimensions: bool = True, show_grid: bool = True,
                         output_path: Optional[str] = None) -> str:
        """
        Render a professional architect-quality floor plan with proper dimensions and labels.
        
        Args:
            floor_plan: FloorPlan object with room layout
            title: Title for the drawing
            show_dimensions: Whether to show detailed dimensions
            show_grid: Whether to show background grid
            output_path: Path to save the image
            
        Returns:
            Base64 encoded image string
        """
        # Calculate overall dimensions
        building_length = floor_plan.total_dimensions.get('length', 50)
        building_width = floor_plan.total_dimensions.get('width', 40)
        total_area = floor_plan.total_dimensions.get('total_area', building_length * building_width)
        
        # Create figure with professional proportions (A3/A2 size ratio)
        fig_width = max(16, building_length * 0.25)
        fig_height = max(12, building_width * 0.25)
        
        fig, ax = plt.subplots(1, 1, figsize=(fig_width, fig_height))
        fig.patch.set_facecolor('white')
        
        # Add professional grid
        if show_grid:
            self._add_professional_grid(ax, building_length, building_width)
        
        # Draw rooms with professional styling
        self._draw_rooms_professional(ax, floor_plan.rooms)
        
        # Draw doors and windows
        if hasattr(floor_plan, 'doors_windows') and floor_plan.doors_windows:
            self._draw_doors_windows_professional(ax, floor_plan.doors_windows)
        
        # Add professional dimensions
        if show_dimensions:
            self._add_professional_dimensions(ax, floor_plan.rooms, building_length, building_width)
        
        # Add professional title block and labels
        self._add_professional_title_block(ax, title, floor_plan, building_length, building_width, total_area)
        
        # Set professional styling
        self._apply_professional_styling(ax, building_length, building_width)
        
        # Save and return
        return self._save_and_encode(fig, output_path)
    
    def _add_professional_grid(self, ax, building_length: float, building_width: float):
        """Add professional architectural grid."""
        # Major grid lines every 5 feet (thick)
        major_x = np.arange(0, building_length + 5, 5)
        major_y = np.arange(0, building_width + 5, 5)
        
        for x in major_x:
            ax.axvline(x, color=self.grid_color, linewidth=0.8, alpha=0.7)
        for y in major_y:
            ax.axhline(y, color=self.grid_color, linewidth=0.8, alpha=0.7)
        
        # Minor grid lines every 1 foot (thin)
        minor_x = np.arange(0, building_length + 1, 1)
        minor_y = np.arange(0, building_width + 1, 1)
        
        for x in minor_x:
            ax.axvline(x, color=self.grid_color, linewidth=0.3, alpha=0.5)
        for y in minor_y:
            ax.axhline(y, color=self.grid_color, linewidth=0.3, alpha=0.5)
    
    def _draw_rooms_professional(self, ax, rooms: Dict[str, RoomDimensions]):
        """Draw rooms with professional architectural styling and specialized elements."""
        for room_name, room in rooms.items():
            # Determine room type for specialized rendering
            room_type = self._get_room_type(room_name)
            
            # Select appropriate fill color based on room type
            fill_color = self._get_room_fill_color(room_type)
            
            # Draw room rectangle with proper wall thickness
            self._draw_room_walls(ax, room, room_type)
            
            # Fill room interior
            interior_rect = Rectangle(
                (room.x_position + self.wall_thickness/2, room.y_position + self.wall_thickness/2),
                room.length - self.wall_thickness, room.width - self.wall_thickness,
                linewidth=0,
                facecolor=fill_color,
                alpha=0.3
            )
            ax.add_patch(interior_rect)
            
            # Add specialized room elements
            self._add_room_specific_elements(ax, room, room_type)
            
            # Add professional room labels
            self._add_professional_room_labels(ax, room, room_name)
    
    def _get_room_type(self, room_name: str) -> str:
        """Determine room type from name."""
        name_lower = room_name.lower()
        if 'stair' in name_lower:
            return 'staircase'
        elif 'balcony' in name_lower:
            return 'balcony'
        elif 'utility' in name_lower or 'store' in name_lower:
            return 'utility'
        elif 'bathroom' in name_lower or 'toilet' in name_lower:
            return 'bathroom'
        elif 'kitchen' in name_lower:
            return 'kitchen'
        elif 'living' in name_lower:
            return 'living_room'
        elif 'bedroom' in name_lower or 'master' in name_lower:
            return 'bedroom'
        elif 'dining' in name_lower:
            return 'dining'
        elif 'pooja' in name_lower:
            return 'pooja_room'
        else:
            return 'general'
    
    def _get_room_fill_color(self, room_type: str) -> str:
        """Get appropriate fill color for room type."""
        color_map = {
            'staircase': self.stair_color,
            'balcony': self.balcony_color,
            'utility': self.utility_color,
            'bathroom': '#E0F6FF',  # Light blue
            'kitchen': '#FFF8DC',   # Cornsilk
            'living_room': self.room_fill_color,
            'bedroom': '#F0F8FF',   # Alice blue
            'dining': '#FDF5E6',    # Old lace
            'pooja_room': '#FFE4E1', # Misty rose
            'general': self.room_fill_color
        }
        return color_map.get(room_type, self.room_fill_color)
    
    def _draw_room_walls(self, ax, room: RoomDimensions, room_type: str):
        """Draw room walls with proper thickness."""
        # Outer wall rectangle (thick black lines)
        outer_rect = Rectangle(
            (room.x_position, room.y_position),
            room.length, room.width,
            linewidth=self.wall_linewidth,
            edgecolor=self.wall_color,
            facecolor='none'
        )
        ax.add_patch(outer_rect)
        
        # Inner wall rectangle (for wall thickness visualization)
        if room_type != 'balcony':  # Balconies typically have different wall treatment
            inner_rect = Rectangle(
                (room.x_position + self.wall_thickness/2, room.y_position + self.wall_thickness/2),
                room.length - self.wall_thickness, room.width - self.wall_thickness,
                linewidth=self.interior_wall_linewidth,
                edgecolor=self.wall_color,
                facecolor='none',
                alpha=0.7
            )
            ax.add_patch(inner_rect)
    
    def _add_room_specific_elements(self, ax, room: RoomDimensions, room_type: str):
        """Add room-specific architectural elements."""
        center_x = room.x_position + room.length / 2
        center_y = room.y_position + room.width / 2
        
        if room_type == 'staircase':
            self._draw_staircase_symbol(ax, room)
        elif room_type == 'bathroom':
            self._draw_bathroom_fixtures(ax, room)
        elif room_type == 'kitchen':
            self._draw_kitchen_elements(ax, room)
        elif room_type == 'balcony':
            self._draw_balcony_elements(ax, room)
    
    def _draw_staircase_symbol(self, ax, room: RoomDimensions):
        """Draw professional staircase symbol."""
        # Calculate stair parameters
        stair_width = min(room.length, room.width) * 0.8
        num_treads = int(stair_width / self.stair_tread_depth)
        
        start_x = room.x_position + (room.length - stair_width) / 2
        start_y = room.y_position + room.width * 0.1
        
        # Draw individual stair treads
        for i in range(num_treads):
            tread_y = start_y + i * self.stair_tread_depth
            if tread_y + self.stair_tread_depth <= room.y_position + room.width * 0.9:
                tread_rect = Rectangle(
                    (start_x, tread_y),
                    stair_width, self.stair_tread_depth * 0.8,
                    linewidth=1,
                    edgecolor=self.stair_color,
                    facecolor=self.stair_color,
                    alpha=0.6
                )
                ax.add_patch(tread_rect)
        
        # Add direction arrow
        arrow_start_x = start_x + stair_width / 2
        arrow_start_y = start_y
        arrow_end_y = start_y + (num_treads - 2) * self.stair_tread_depth
        
        ax.annotate('', xy=(arrow_start_x, arrow_end_y), xytext=(arrow_start_x, arrow_start_y),
                   arrowprops=dict(arrowstyle='->', lw=2, color=self.stair_color))
        
        # Add "UP" label
        ax.text(arrow_start_x + 1, (arrow_start_y + arrow_end_y) / 2, 'UP',
               ha='left', va='center', fontsize=self.area_fontsize,
               fontweight='bold', color=self.stair_color)
    
    def _draw_bathroom_fixtures(self, ax, room: RoomDimensions):
        """Draw bathroom fixtures."""
        # Toilet (small rectangle in corner)
        toilet_size = 1.5
        toilet_x = room.x_position + room.length - toilet_size - 0.5
        toilet_y = room.y_position + 0.5
        
        toilet_rect = Rectangle(
            (toilet_x, toilet_y), toilet_size, toilet_size,
            linewidth=1, edgecolor='black', facecolor='white'
        )
        ax.add_patch(toilet_rect)
        
        # Washbasin (circle)
        basin_x = room.x_position + 1.5
        basin_y = room.y_position + room.width - 1.5
        basin_circle = Circle((basin_x, basin_y), 0.7, 
                            linewidth=1, edgecolor='black', facecolor='lightblue', alpha=0.5)
        ax.add_patch(basin_circle)
    
    def _draw_kitchen_elements(self, ax, room: RoomDimensions):
        """Draw kitchen elements."""
        # Kitchen counter (L-shaped or straight)
        counter_width = 2.0
        
        # Main counter along one wall
        counter_rect = Rectangle(
            (room.x_position + 0.5, room.y_position + 0.5),
            room.length - 1.0, counter_width,
            linewidth=1, edgecolor='brown', facecolor='burlywood', alpha=0.7
        )
        ax.add_patch(counter_rect)
        
        # Side counter if room is large enough
        if room.width > 8:
            side_counter_rect = Rectangle(
                (room.x_position + 0.5, room.y_position + 0.5),
                counter_width, room.width - 1.0,
                linewidth=1, edgecolor='brown', facecolor='burlywood', alpha=0.7
            )
            ax.add_patch(side_counter_rect)
    
    def _draw_balcony_elements(self, ax, room: RoomDimensions):
        """Draw balcony elements."""
        # Balcony railing (dashed line along open edge)
        # Assuming balcony opens to the front (adjust based on orientation)
        railing_y = room.y_position + room.width
        ax.plot([room.x_position, room.x_position + room.length], 
               [railing_y, railing_y], 
               linestyle='--', linewidth=2, color='gray', alpha=0.8)
        
        # Add small plants or decorative elements
        for i in range(int(room.length / 4)):
            plant_x = room.x_position + (i + 1) * room.length / (int(room.length / 4) + 1)
            plant_y = room.y_position + room.width / 2
            plant_circle = Circle((plant_x, plant_y), 0.3, 
                                linewidth=1, edgecolor='green', facecolor='lightgreen', alpha=0.6)
            ax.add_patch(plant_circle)
    
    def _add_professional_room_labels(self, ax, room: RoomDimensions, room_name: str):
        """Add professional room labels with dimensions and area."""
        room_area = room.length * room.width
        center_x = room.x_position + room.length / 2
        center_y = room.y_position + room.width / 2
        
        # Clean room name
        clean_name = room_name.replace('_', ' ').title()
        
        # Room name (bold, larger)
        ax.text(center_x, center_y + 1.2, clean_name,
               ha='center', va='center', fontsize=self.room_label_fontsize,
               fontweight='bold', color=self.text_color)
        
        # Room dimensions
        ax.text(center_x, center_y, f"{room.length:.1f}' × {room.width:.1f}'",
               ha='center', va='center', fontsize=self.area_fontsize,
               color=self.text_color, style='italic')
        
        # Room area
        ax.text(center_x, center_y - 1.2, f"{room_area:.0f} sq.ft",
               ha='center', va='center', fontsize=self.area_fontsize,
               color=self.text_color, bbox=dict(boxstyle="round,pad=0.3", 
               facecolor='white', edgecolor='gray', alpha=0.9))
    
    def _draw_doors_windows_professional(self, ax, doors_windows: List[DoorWindow]):
        """Draw doors and windows with professional symbols."""
        for item in doors_windows:
            if item.type.lower() == 'door':
                self._draw_door_symbol(ax, item)
            elif item.type.lower() == 'window':
                self._draw_window_symbol(ax, item)
    
    def _draw_door_symbol(self, ax, door: DoorWindow):
        """Draw professional door symbol with proper swing representation."""
        # Door opening (gap in wall) - more realistic representation
        wall_direction = door.wall.lower()
        
        if wall_direction in ['north', 'south']:
            # Horizontal door opening
            door_opening = Rectangle(
                (door.x_position - door.width/2, door.y_position - self.wall_thickness/2),
                door.width, self.wall_thickness,
                linewidth=0,
                facecolor='white',
                alpha=1.0
            )
            ax.add_patch(door_opening)
            
            # Door swing arc (90-degree swing)
            swing_radius = door.width * 0.9
            if wall_direction == 'north':
                arc = patches.Arc((door.x_position - door.width/2, door.y_position), 
                                swing_radius * 2, swing_radius * 2,
                                angle=0, theta1=0, theta2=90,
                                linewidth=2, color=self.door_color)
            else:  # south
                arc = patches.Arc((door.x_position + door.width/2, door.y_position), 
                                swing_radius * 2, swing_radius * 2,
                                angle=180, theta1=0, theta2=90,
                                linewidth=2, color=self.door_color)
        else:
            # Vertical door opening
            door_opening = Rectangle(
                (door.x_position - self.wall_thickness/2, door.y_position - door.width/2),
                self.wall_thickness, door.width,
                linewidth=0,
                facecolor='white',
                alpha=1.0
            )
            ax.add_patch(door_opening)
            
            # Door swing arc
            swing_radius = door.width * 0.9
            if wall_direction == 'east':
                arc = patches.Arc((door.x_position, door.y_position - door.width/2), 
                                swing_radius * 2, swing_radius * 2,
                                angle=90, theta1=0, theta2=90,
                                linewidth=2, color=self.door_color)
            else:  # west
                arc = patches.Arc((door.x_position, door.y_position + door.width/2), 
                                swing_radius * 2, swing_radius * 2,
                                angle=270, theta1=0, theta2=90,
                                linewidth=2, color=self.door_color)
        
        ax.add_patch(arc)
        
        # Add door leaf line (closed position)
        if wall_direction in ['north', 'south']:
            door_leaf_x = door.x_position - door.width/2 if wall_direction == 'north' else door.x_position + door.width/2
            ax.plot([door_leaf_x, door_leaf_x], 
                   [door.y_position - self.wall_thickness/2, door.y_position + self.wall_thickness/2],
                   linewidth=3, color=self.door_color, alpha=0.8)
        else:
            door_leaf_y = door.y_position - door.width/2 if wall_direction == 'east' else door.y_position + door.width/2
            ax.plot([door.x_position - self.wall_thickness/2, door.x_position + self.wall_thickness/2],
                   [door_leaf_y, door_leaf_y],
                   linewidth=3, color=self.door_color, alpha=0.8)
    
    def _draw_window_symbol(self, ax, window: DoorWindow):
        """Draw professional window symbol with proper frame representation."""
        wall_direction = window.wall.lower()
        
        if wall_direction in ['north', 'south']:
            # Horizontal window
            # Window opening in wall
            window_opening = Rectangle(
                (window.x_position - window.width/2, window.y_position - self.wall_thickness/2),
                window.width, self.wall_thickness,
                linewidth=0,
                facecolor='lightblue',
                alpha=0.3
            )
            ax.add_patch(window_opening)
            
            # Window frame (double lines for glass)
            frame_offset = self.wall_thickness * 0.2
            ax.plot([window.x_position - window.width/2, window.x_position + window.width/2],
                   [window.y_position - frame_offset, window.y_position - frame_offset],
                   linewidth=2, color=self.window_color)
            ax.plot([window.x_position - window.width/2, window.x_position + window.width/2],
                   [window.y_position + frame_offset, window.y_position + frame_offset],
                   linewidth=2, color=self.window_color)
            
            # Window mullions (vertical dividers)
            num_panels = max(1, int(window.width / 3))
            for i in range(1, num_panels):
                mullion_x = window.x_position - window.width/2 + i * (window.width / num_panels)
                ax.plot([mullion_x, mullion_x],
                       [window.y_position - frame_offset, window.y_position + frame_offset],
                       linewidth=1, color=self.window_color, alpha=0.7)
        else:
            # Vertical window
            # Window opening in wall
            window_opening = Rectangle(
                (window.x_position - self.wall_thickness/2, window.y_position - window.width/2),
                self.wall_thickness, window.width,
                linewidth=0,
                facecolor='lightblue',
                alpha=0.3
            )
            ax.add_patch(window_opening)
            
            # Window frame (double lines for glass)
            frame_offset = self.wall_thickness * 0.2
            ax.plot([window.x_position - frame_offset, window.x_position - frame_offset],
                   [window.y_position - window.width/2, window.y_position + window.width/2],
                   linewidth=2, color=self.window_color)
            ax.plot([window.x_position + frame_offset, window.x_position + frame_offset],
                   [window.y_position - window.width/2, window.y_position + window.width/2],
                   linewidth=2, color=self.window_color)
            
            # Window mullions (horizontal dividers)
            num_panels = max(1, int(window.width / 3))
            for i in range(1, num_panels):
                mullion_y = window.y_position - window.width/2 + i * (window.width / num_panels)
                ax.plot([window.x_position - frame_offset, window.x_position + frame_offset],
                       [mullion_y, mullion_y],
                       linewidth=1, color=self.window_color, alpha=0.7)
    
    def _add_professional_dimensions(self, ax, rooms: Dict[str, RoomDimensions], 
                                   building_length: float, building_width: float):
        """Add professional dimension lines with arrows and measurements."""
        
        # Overall building dimensions
        # Bottom dimension (total length)
        y_pos = -self.dimension_offset
        self._draw_dimension_line(ax, 0, y_pos, building_length, y_pos, f"{building_length:.1f}'")
        
        # Left dimension (total width)
        x_pos = -self.dimension_offset
        self._draw_dimension_line(ax, x_pos, 0, x_pos, building_width, f"{building_width:.1f}'", vertical=True)
        
        # Individual room dimensions (sample for major rooms)
        for room_name, room in rooms.items():
            if 'living' in room_name.lower() or 'bedroom' in room_name.lower() or 'kitchen' in room_name.lower():
                # Room length dimension (top)
                y_pos = room.y_position + room.width + 1.0
                x_start = room.x_position
                x_end = room.x_position + room.length
                self._draw_dimension_line(ax, x_start, y_pos, x_end, y_pos, f"{room.length:.1f}'")
                
                # Room width dimension (right)
                x_pos = room.x_position + room.length + 1.0
                y_start = room.y_position
                y_end = room.y_position + room.width
                self._draw_dimension_line(ax, x_pos, y_start, x_pos, y_end, f"{room.width:.1f}'", vertical=True)
    
    def _draw_dimension_line(self, ax, x1: float, y1: float, x2: float, y2: float, 
                           text: str, vertical: bool = False):
        """Draw a professional dimension line with arrows and text."""
        # Main dimension line
        ax.plot([x1, x2], [y1, y2], color=self.dimension_color, linewidth=1.0)
        
        # Extension lines
        if vertical:
            # Vertical dimension
            ax.plot([x1 - self.dimension_extension/2, x1 + self.dimension_extension/2], 
                   [y1, y1], color=self.dimension_line_color, linewidth=0.8)
            ax.plot([x2 - self.dimension_extension/2, x2 + self.dimension_extension/2], 
                   [y2, y2], color=self.dimension_line_color, linewidth=0.8)
            
            # Text
            mid_y = (y1 + y2) / 2
            ax.text(x1 - 0.5, mid_y, text, ha='center', va='center', 
                   fontsize=self.dimension_fontsize, color=self.dimension_color,
                   rotation=90, fontweight='bold')
        else:
            # Horizontal dimension
            ax.plot([x1, x1], [y1 - self.dimension_extension/2, y1 + self.dimension_extension/2], 
                   color=self.dimension_line_color, linewidth=0.8)
            ax.plot([x2, x2], [y2 - self.dimension_extension/2, y2 + self.dimension_extension/2], 
                   color=self.dimension_line_color, linewidth=0.8)
            
            # Text
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y1 - 0.5, text, ha='center', va='center', 
                   fontsize=self.dimension_fontsize, color=self.dimension_color,
                   fontweight='bold')
        
        # Arrow heads
        arrow_length = self.arrow_size
        if vertical:
            # Vertical arrows
            ax.arrow(x1, y1, 0, arrow_length, head_width=0.2, head_length=0.2, 
                    fc=self.dimension_color, ec=self.dimension_color)
            ax.arrow(x2, y2, 0, -arrow_length, head_width=0.2, head_length=0.2, 
                    fc=self.dimension_color, ec=self.dimension_color)
        else:
            # Horizontal arrows
            ax.arrow(x1, y1, arrow_length, 0, head_width=0.2, head_length=0.2, 
                    fc=self.dimension_color, ec=self.dimension_color)
            ax.arrow(x2, y2, -arrow_length, 0, head_width=0.2, head_length=0.2, 
                    fc=self.dimension_color, ec=self.dimension_color)
    
    def _add_professional_title_block(self, ax, title: str, floor_plan: FloorPlan, 
                                    building_length: float, building_width: float, total_area: float):
        """Add professional architect's title block matching industry standards."""
        # Title block position (top-right corner)
        title_width = 18
        title_height = 12
        title_x = building_length - title_width - 2
        title_y = building_width + 3
        
        # Main title block rectangle with professional border
        title_rect = Rectangle(
            (title_x, title_y), title_width, title_height,
            linewidth=2.5,
            edgecolor=self.text_color,
            facecolor=self.title_box_color,
            alpha=0.95
        )
        ax.add_patch(title_rect)
        
        # Inner border for professional look
        inner_rect = Rectangle(
            (title_x + 0.3, title_y + 0.3), title_width - 0.6, title_height - 0.6,
            linewidth=1,
            edgecolor=self.text_color,
            facecolor='none'
        )
        ax.add_patch(inner_rect)
        
        # Title header
        ax.text(title_x + title_width/2, title_y + title_height - 1.5, "Architectural Floor Plan",
               ha='center', va='center', fontsize=self.title_fontsize, 
               fontweight='bold', color=self.text_color)
        
        # Floor information with professional naming
        floor_names = {
            0: "Ground Floor",
            1: "First Floor", 
            2: "Second Floor",
            3: "Third Floor"
        }
        floor_text = floor_names.get(floor_plan.floor_number, f"Floor {floor_plan.floor_number + 1}")
        ax.text(title_x + title_width/2, title_y + title_height - 3, floor_text,
               ha='center', va='center', fontsize=self.subtitle_fontsize, 
               fontweight='bold', color=self.text_color,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.4))
        
        # Building specifications in organized rows
        specs_start_y = title_y + title_height - 5
        line_height = 1.2
        
        # Building dimensions
        ax.text(title_x + 1, specs_start_y, f"Building Size: {building_length:.1f}' × {building_width:.1f}'",
               ha='left', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Total area
        ax.text(title_x + 1, specs_start_y - line_height, f"Total Area: {total_area:.0f} sq.ft",
               ha='left', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Room count
        room_count = len(floor_plan.rooms)
        ax.text(title_x + 1, specs_start_y - 2*line_height, f"Rooms: {room_count}",
               ha='left', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Scale information
        ax.text(title_x + 1, specs_start_y - 3*line_height, "Scale: 1\" = 1'",
               ha='left', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Date
        from datetime import datetime
        date_str = datetime.now().strftime("%m/%d/%Y")
        ax.text(title_x + 1, specs_start_y - 4*line_height, f"Date: {date_str}",
               ha='left', va='center', fontsize=self.area_fontsize, color=self.text_color)
        
        # Professional compass rose (top-left)
        north_x, north_y = 4, building_width + 8
        self._draw_professional_compass_rose(ax, north_x, north_y)
    
    def _draw_professional_compass_rose(self, ax, x: float, y: float):
        """Draw professional compass rose matching industry standards."""
        # Outer circle
        outer_circle = Circle((x, y), 2.5, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(outer_circle)
        
        # Inner circle
        inner_circle = Circle((x, y), 1.8, fill=False, edgecolor='black', linewidth=1)
        ax.add_patch(inner_circle)
        
        # North arrow (main)
        north_points = np.array([[x, y + 2.2], [x - 0.3, y + 1.5], [x, y + 1.8], [x + 0.3, y + 1.5]])
        north_arrow = patches.Polygon(north_points, closed=True, facecolor='black', edgecolor='black')
        ax.add_patch(north_arrow)
        
        # South arrow (smaller)
        south_points = np.array([[x, y - 2.2], [x - 0.2, y - 1.5], [x, y - 1.8], [x + 0.2, y - 1.5]])
        south_arrow = patches.Polygon(south_points, closed=True, facecolor='white', edgecolor='black')
        ax.add_patch(south_arrow)
        
        # East and West indicators
        ax.plot([x + 1.5, x + 2.2], [y, y], linewidth=2, color='black')
        ax.plot([x - 1.5, x - 2.2], [y, y], linewidth=2, color='black')
        
        # Cardinal direction labels
        ax.text(x, y + 3.2, 'N', ha='center', va='center', 
               fontsize=self.subtitle_fontsize, fontweight='bold')
        ax.text(x + 3.2, y, 'E', ha='center', va='center', 
               fontsize=self.label_fontsize, fontweight='bold')
        ax.text(x, y - 3.2, 'S', ha='center', va='center', 
               fontsize=self.label_fontsize, fontweight='bold')
        ax.text(x - 3.2, y, 'W', ha='center', va='center', 
               fontsize=self.label_fontsize, fontweight='bold')
    
    def _draw_north_arrow(self, ax, x: float, y: float):
        """Draw simple north arrow (legacy method)."""
        # Arrow shaft
        ax.arrow(x, y, 0, 2, head_width=0.3, head_length=0.3, 
                fc='black', ec='black', linewidth=2)
        
        # "N" label
        ax.text(x, y + 2.8, 'N', ha='center', va='center', 
               fontsize=self.label_fontsize, fontweight='bold')
        
        # Circle
        circle = Circle((x, y + 1), 0.8, fill=False, edgecolor='black', linewidth=1.5)
        ax.add_patch(circle)
    
    def _apply_professional_styling(self, ax, building_length: float, building_width: float):
        """Apply professional architectural drawing styling."""
        # Set limits with margins for dimensions
        margin = 5
        ax.set_xlim(-margin, building_length + margin)
        ax.set_ylim(-margin, building_width + margin + 10)  # Extra space for title block
        
        # Equal aspect ratio
        ax.set_aspect('equal')
        
        # Remove axes for clean look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Clean spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # White background
        ax.set_facecolor('white')
    
    def _save_and_encode(self, fig, output_path: Optional[str]) -> str:
        """Save figure and return base64 encoded string."""
        # Save to file if path provided
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', format='png')
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return image_base64
