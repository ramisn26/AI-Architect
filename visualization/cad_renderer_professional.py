"""
Professional Architect's Blueprint Renderer for architectural designs.
Creates certified architect-quality floor plans with proper dimensions and labels.
"""

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
        self.wall_linewidth = 2.5
        self.room_fill_color = '#FFFFFF'  # White interior
        self.room_edge_color = '#000000'
        self.dimension_color = '#FF0000'  # Red dimensions (standard)
        self.dimension_line_color = '#000000'
        self.text_color = '#000000'
        self.grid_color = '#E0E0E0'  # Light grid
        self.door_color = '#8B4513'  # Brown doors
        self.window_color = '#4169E1'  # Blue windows
        self.title_box_color = '#F0F8FF'
        
        # Professional font settings
        self.title_fontsize = 14
        self.subtitle_fontsize = 12
        self.label_fontsize = 10
        self.dimension_fontsize = 8
        self.room_label_fontsize = 9
        self.area_fontsize = 8
        
        # Dimension settings
        self.dimension_offset = 2.5  # Distance from walls
        self.dimension_extension = 1.5  # Extension line length
        self.arrow_size = 0.4
        
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
        """Draw rooms with professional architectural styling."""
        for room_name, room in rooms.items():
            # Draw room rectangle with thick walls
            rect = Rectangle(
                (room.x_position, room.y_position),
                room.length, room.width,
                linewidth=self.wall_linewidth,
                edgecolor=self.wall_color,
                facecolor=self.room_fill_color,
                alpha=0.9
            )
            ax.add_patch(rect)
            
            # Add room label with area
            room_area = room.length * room.width
            center_x = room.x_position + room.length / 2
            center_y = room.y_position + room.width / 2
            
            # Room name (bold, larger)
            ax.text(center_x, center_y + 0.8, room_name.replace('_', ' ').title(),
                   ha='center', va='center', fontsize=self.room_label_fontsize,
                   fontweight='bold', color=self.text_color)
            
            # Room dimensions
            ax.text(center_x, center_y, f"{room.length:.1f}' × {room.width:.1f}'",
                   ha='center', va='center', fontsize=self.area_fontsize,
                   color=self.text_color, style='italic')
            
            # Room area
            ax.text(center_x, center_y - 0.8, f"{room_area:.0f} sq.ft",
                   ha='center', va='center', fontsize=self.area_fontsize,
                   color=self.text_color, bbox=dict(boxstyle="round,pad=0.2", 
                   facecolor='white', edgecolor='gray', alpha=0.8))
    
    def _draw_doors_windows_professional(self, ax, doors_windows: List[DoorWindow]):
        """Draw doors and windows with professional symbols."""
        for item in doors_windows:
            if item.type.lower() == 'door':
                self._draw_door_symbol(ax, item)
            elif item.type.lower() == 'window':
                self._draw_window_symbol(ax, item)
    
    def _draw_door_symbol(self, ax, door: DoorWindow):
        """Draw professional door symbol."""
        # Door opening (gap in wall)
        door_rect = Rectangle(
            (door.x_position - door.width/2, door.y_position - 0.2),
            door.width, 0.4,
            linewidth=0,
            facecolor='white',
            alpha=1.0
        )
        ax.add_patch(door_rect)
        
        # Door swing arc
        if door.wall.lower() in ['north', 'south']:
            # Horizontal door
            arc = patches.Arc((door.x_position, door.y_position), 
                            door.width * 2, door.width * 2,
                            angle=0, theta1=0, theta2=90,
                            linewidth=1.5, color=self.door_color)
        else:
            # Vertical door
            arc = patches.Arc((door.x_position, door.y_position), 
                            door.width * 2, door.width * 2,
                            angle=90, theta1=0, theta2=90,
                            linewidth=1.5, color=self.door_color)
        ax.add_patch(arc)
    
    def _draw_window_symbol(self, ax, window: DoorWindow):
        """Draw professional window symbol."""
        # Window opening
        if window.wall.lower() in ['north', 'south']:
            # Horizontal window
            window_rect = Rectangle(
                (window.x_position - window.width/2, window.y_position - 0.1),
                window.width, 0.2,
                linewidth=2,
                edgecolor=self.window_color,
                facecolor='lightblue',
                alpha=0.7
            )
        else:
            # Vertical window
            window_rect = Rectangle(
                (window.x_position - 0.1, window.y_position - window.width/2),
                0.2, window.width,
                linewidth=2,
                edgecolor=self.window_color,
                facecolor='lightblue',
                alpha=0.7
            )
        ax.add_patch(window_rect)
    
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
        """Add professional architect's title block."""
        # Title block position (top-right)
        title_x = building_length - 15
        title_y = building_width + 5
        
        # Title block rectangle
        title_rect = FancyBboxPatch(
            (title_x, title_y), 14, 8,
            boxstyle="round,pad=0.3",
            facecolor=self.title_box_color,
            edgecolor=self.text_color,
            linewidth=1.5
        )
        ax.add_patch(title_rect)
        
        # Title text
        ax.text(title_x + 7, title_y + 6.5, title, ha='center', va='center',
               fontsize=self.title_fontsize, fontweight='bold', color=self.text_color)
        
        # Floor information
        floor_text = f"Ground Floor" if floor_plan.floor_number == 0 else f"Floor {floor_plan.floor_number + 1}"
        ax.text(title_x + 7, title_y + 5.5, floor_text, ha='center', va='center',
               fontsize=self.subtitle_fontsize, color=self.text_color)
        
        # Building dimensions
        ax.text(title_x + 7, title_y + 4.5, f"Building Size: {building_length:.1f}' × {building_width:.1f}'",
               ha='center', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Total area
        ax.text(title_x + 7, title_y + 3.5, f"Total Area: {total_area:.0f} sq.ft",
               ha='center', va='center', fontsize=self.label_fontsize, color=self.text_color)
        
        # Scale
        ax.text(title_x + 7, title_y + 2.5, "Scale: 1\" = 1'", ha='center', va='center',
               fontsize=self.label_fontsize, color=self.text_color)
        
        # Date
        from datetime import datetime
        date_str = datetime.now().strftime("%m/%d/%Y")
        ax.text(title_x + 7, title_y + 1.5, f"Date: {date_str}", ha='center', va='center',
               fontsize=self.area_fontsize, color=self.text_color)
        
        # North arrow (top-left)
        north_x, north_y = 3, building_width + 3
        self._draw_north_arrow(ax, north_x, north_y)
    
    def _draw_north_arrow(self, ax, x: float, y: float):
        """Draw professional north arrow."""
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
