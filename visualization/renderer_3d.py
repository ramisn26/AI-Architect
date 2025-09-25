"""
Professional 3D Architectural Renderer
Creates photorealistic 3D visualizations of architectural designs with interactive controls.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import base64
import io
import json
import math

# Set matplotlib backend for compatibility
import matplotlib
matplotlib.use('Agg')

import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from architectural_engine.schemas import FloorPlan, RoomDimensions, ArchitecturalDesign

class Renderer3D:
    """Professional 3D architectural renderer with photorealistic visualization."""
    
    def __init__(self):
        """Initialize 3D renderer with professional settings."""
        # Color schemes for different room types
        self.room_colors = {
            'living_room': '#8B4513',      # Saddle Brown
            'kitchen': '#FF6347',          # Tomato
            'bedroom': '#4682B4',          # Steel Blue
            'master_bedroom': '#191970',   # Midnight Blue
            'bathroom': '#20B2AA',         # Light Sea Green
            'dining_room': '#DAA520',      # Goldenrod
            'balcony': '#32CD32',          # Lime Green
            'staircase': '#696969',        # Dim Gray
            'corridor': '#D3D3D3',         # Light Gray
            'utility': '#808080',          # Gray
            'parking': '#2F4F4F',          # Dark Slate Gray
            'pooja_room': '#FFD700',       # Gold
            'study_room': '#800080',       # Purple
            'guest_bedroom': '#4169E1',    # Royal Blue
            'family_room': '#CD853F',      # Peru
            'storage': '#A0A0A0'           # Gray
        }
        
        # Material properties for realistic rendering
        self.materials = {
            'wall': {'color': '#F5F5DC', 'opacity': 0.8},
            'floor': {'color': '#DEB887', 'opacity': 0.9},
            'ceiling': {'color': '#FFFFFF', 'opacity': 0.7},
            'door': {'color': '#8B4513', 'opacity': 0.9},
            'window': {'color': '#87CEEB', 'opacity': 0.3}
        }
        
        # Standard dimensions
        self.wall_thickness = 0.5  # feet
        self.floor_height = 10.0   # feet
        self.door_height = 7.0     # feet
        self.window_height = 4.0   # feet
        
    def render_3d_building(self, design: ArchitecturalDesign, 
                          all_floor_plans: List[FloorPlan],
                          view_mode: str = 'interactive') -> str:
        """
        Render complete 3D building with all floors.
        
        Args:
            design: Complete architectural design
            all_floor_plans: List of floor plans for all floors
            view_mode: 'interactive', 'static', or 'export'
            
        Returns:
            str: Base64 encoded HTML or image data
        """
        fig = go.Figure()
        
        # Calculate building dimensions
        setbacks = design.setbacks
        land_side = design.input_parameters.land_size ** 0.5
        building_length = land_side - setbacks.front - setbacks.rear
        building_width = land_side - setbacks.left - setbacks.right
        
        # Render each floor
        for floor_idx, floor_plan in enumerate(all_floor_plans):
            floor_height_offset = floor_idx * self.floor_height
            
            # Add floor slab
            self._add_floor_slab(fig, building_length, building_width, 
                               floor_height_offset, floor_idx)
            
            # Add rooms for this floor
            self._add_floor_rooms(fig, floor_plan, floor_height_offset, floor_idx)
            
            # Add walls
            self._add_exterior_walls(fig, building_length, building_width, 
                                   floor_height_offset, floor_idx)
        
        # Add roof
        total_height = len(all_floor_plans) * self.floor_height
        self._add_roof(fig, building_length, building_width, total_height)
        
        # Configure 3D scene
        self._configure_3d_scene(fig, building_length, building_width, total_height)
        
        # Add professional lighting and camera
        self._add_professional_lighting(fig)
        
        if view_mode == 'interactive':
            return self._export_interactive_html(fig, design)
        elif view_mode == 'static':
            return self._export_static_image(fig)
        else:
            return self._export_for_download(fig, design)
    
    def render_floor_3d(self, floor_plan: FloorPlan, floor_number: int = 0,
                       show_furniture: bool = True) -> str:
        """
        Render single floor in 3D with optional furniture.
        
        Args:
            floor_plan: Floor plan to render
            floor_number: Floor number (0 = ground floor)
            show_furniture: Whether to show basic furniture
            
        Returns:
            str: Base64 encoded HTML data
        """
        fig = go.Figure()
        
        # Calculate floor dimensions
        total_dims = floor_plan.total_dimensions
        building_length = total_dims.get('building_length', 40)
        building_width = total_dims.get('building_width', 30)
        
        floor_height_offset = floor_number * self.floor_height
        
        # Add floor slab
        self._add_floor_slab(fig, building_length, building_width, 
                           floor_height_offset, floor_number)
        
        # Add rooms
        self._add_floor_rooms(fig, floor_plan, floor_height_offset, floor_number)
        
        # Add exterior walls
        self._add_exterior_walls(fig, building_length, building_width, 
                               floor_height_offset, floor_number)
        
        # Add furniture if requested
        if show_furniture:
            self._add_basic_furniture(fig, floor_plan, floor_height_offset)
        
        # Configure scene
        self._configure_3d_scene(fig, building_length, building_width, self.floor_height)
        self._add_professional_lighting(fig)
        
        return self._export_interactive_html(fig, None, f"Floor {floor_number + 1}")
    
    def _add_floor_slab(self, fig: go.Figure, length: float, width: float, 
                       height_offset: float, floor_number: int):
        """Add floor slab (concrete base)."""
        # Floor slab vertices
        x = [0, length, length, 0, 0, length, length, 0]
        y = [0, 0, width, width, 0, 0, width, width]
        z = [height_offset, height_offset, height_offset, height_offset,
             height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5]
        
        # Floor slab faces
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        floor_name = f"Floor {floor_number + 1} Slab"
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=self.materials['floor']['color'],
            opacity=self.materials['floor']['opacity'],
            name=floor_name,
            showlegend=True
        ))
    
    def _add_floor_rooms(self, fig: go.Figure, floor_plan: FloorPlan, 
                        height_offset: float, floor_number: int):
        """Add individual rooms as 3D spaces."""
        for room_name, room_dims in floor_plan.rooms.items():
            if isinstance(room_dims, dict):
                # Handle dictionary format
                length = room_dims.get('length', 10)
                width = room_dims.get('width', 10)
                x_pos = room_dims.get('x_position', 0)
                y_pos = room_dims.get('y_position', 0)
            else:
                # Handle RoomDimensions object (default case)
                length = getattr(room_dims, 'length', 10)
                width = getattr(room_dims, 'width', 10)
                x_pos = getattr(room_dims, 'x_position', 0)
                y_pos = getattr(room_dims, 'y_position', 0)
            
            # Get room color
            room_color = self.room_colors.get(room_name.lower(), '#87CEEB')
            
            # Create room box
            self._add_room_box(fig, x_pos, y_pos, length, width, 
                             height_offset, room_color, room_name, floor_number)
    
    def _add_room_box(self, fig: go.Figure, x_pos: float, y_pos: float,
                     length: float, width: float, height_offset: float,
                     color: str, room_name: str, floor_number: int):
        """Add a single room as a 3D box."""
        # Room vertices
        x = [x_pos, x_pos + length, x_pos + length, x_pos,
             x_pos, x_pos + length, x_pos + length, x_pos]
        y = [y_pos, y_pos, y_pos + width, y_pos + width,
             y_pos, y_pos, y_pos + width, y_pos + width]
        z = [height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5,
             height_offset + self.floor_height, height_offset + self.floor_height, 
             height_offset + self.floor_height, height_offset + self.floor_height]
        
        # Room faces
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        display_name = f"{room_name.replace('_', ' ').title()} (Floor {floor_number + 1})"
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=color,
            opacity=0.6,
            name=display_name,
            showlegend=True,
            hovertemplate=f"<b>{display_name}</b><br>" +
                         f"Size: {length:.1f}' × {width:.1f}'<br>" +
                         f"Area: {length * width:.0f} sq.ft<extra></extra>"
        ))
    
    def _add_exterior_walls(self, fig: go.Figure, length: float, width: float,
                          height_offset: float, floor_number: int):
        """Add exterior walls."""
        wall_height = self.floor_height
        
        # Front wall
        self._add_wall(fig, 0, 0, length, 0, height_offset, wall_height, 
                      f"Front Wall (Floor {floor_number + 1})")
        
        # Back wall
        self._add_wall(fig, 0, width, length, width, height_offset, wall_height,
                      f"Back Wall (Floor {floor_number + 1})")
        
        # Left wall
        self._add_wall(fig, 0, 0, 0, width, height_offset, wall_height,
                      f"Left Wall (Floor {floor_number + 1})")
        
        # Right wall
        self._add_wall(fig, length, 0, length, width, height_offset, wall_height,
                      f"Right Wall (Floor {floor_number + 1})")
    
    def _add_wall(self, fig: go.Figure, x1: float, y1: float, x2: float, y2: float,
                 height_offset: float, wall_height: float, name: str):
        """Add a single wall."""
        thickness = self.wall_thickness
        
        # Calculate wall direction
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        # Normalize direction
        dx /= length
        dy /= length
        
        # Perpendicular direction for thickness
        px = -dy * thickness / 2
        py = dx * thickness / 2
        
        # Wall vertices
        x = [x1 + px, x2 + px, x2 - px, x1 - px,
             x1 + px, x2 + px, x2 - px, x1 - px]
        y = [y1 + py, y2 + py, y2 - py, y1 - py,
             y1 + py, y2 + py, y2 - py, y1 - py]
        z = [height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5,
             height_offset + wall_height, height_offset + wall_height, 
             height_offset + wall_height, height_offset + wall_height]
        
        # Wall faces
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=self.materials['wall']['color'],
            opacity=self.materials['wall']['opacity'],
            name=name,
            showlegend=False
        ))
    
    def _add_roof(self, fig: go.Figure, length: float, width: float, total_height: float):
        """Add roof structure."""
        roof_thickness = 0.5
        
        # Roof vertices
        x = [0, length, length, 0, 0, length, length, 0]
        y = [0, 0, width, width, 0, 0, width, width]
        z = [total_height, total_height, total_height, total_height,
             total_height + roof_thickness, total_height + roof_thickness, 
             total_height + roof_thickness, total_height + roof_thickness]
        
        # Roof faces
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='#8B4513',  # Brown roof
            opacity=0.8,
            name="Roof",
            showlegend=True
        ))
    
    def _add_basic_furniture(self, fig: go.Figure, floor_plan: FloorPlan, 
                           height_offset: float):
        """Add basic furniture to rooms."""
        for room_name, room_dims in floor_plan.rooms.items():
            if isinstance(room_dims, dict):
                length = room_dims.get('length', 10)
                width = room_dims.get('width', 10)
                x_pos = room_dims.get('x_position', 0)
                y_pos = room_dims.get('y_position', 0)
            else:
                length = room_dims.length
                width = room_dims.width
                x_pos = room_dims.x_position
                y_pos = room_dims.y_position
            
            # Add furniture based on room type
            if 'bedroom' in room_name.lower():
                self._add_bed(fig, x_pos + 1, y_pos + 1, height_offset)
            elif 'living' in room_name.lower():
                self._add_sofa(fig, x_pos + 2, y_pos + 2, height_offset)
            elif 'kitchen' in room_name.lower():
                self._add_kitchen_counter(fig, x_pos + 0.5, y_pos + 0.5, 
                                        min(length - 1, 6), height_offset)
    
    def _add_bed(self, fig: go.Figure, x_pos: float, y_pos: float, height_offset: float):
        """Add a bed to the room."""
        bed_length, bed_width, bed_height = 6, 4, 2
        
        x = [x_pos, x_pos + bed_length, x_pos + bed_length, x_pos,
             x_pos, x_pos + bed_length, x_pos + bed_length, x_pos]
        y = [y_pos, y_pos, y_pos + bed_width, y_pos + bed_width,
             y_pos, y_pos, y_pos + bed_width, y_pos + bed_width]
        z = [height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5,
             height_offset + bed_height, height_offset + bed_height, 
             height_offset + bed_height, height_offset + bed_height]
        
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='#8B4513',
            opacity=0.7,
            name="Bed",
            showlegend=False
        ))
    
    def _add_sofa(self, fig: go.Figure, x_pos: float, y_pos: float, height_offset: float):
        """Add a sofa to the room."""
        sofa_length, sofa_width, sofa_height = 5, 2, 2.5
        
        x = [x_pos, x_pos + sofa_length, x_pos + sofa_length, x_pos,
             x_pos, x_pos + sofa_length, x_pos + sofa_length, x_pos]
        y = [y_pos, y_pos, y_pos + sofa_width, y_pos + sofa_width,
             y_pos, y_pos, y_pos + sofa_width, y_pos + sofa_width]
        z = [height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5,
             height_offset + sofa_height, height_offset + sofa_height, 
             height_offset + sofa_height, height_offset + sofa_height]
        
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='#4682B4',
            opacity=0.7,
            name="Sofa",
            showlegend=False
        ))
    
    def _add_kitchen_counter(self, fig: go.Figure, x_pos: float, y_pos: float,
                           counter_length: float, height_offset: float):
        """Add kitchen counter."""
        counter_width, counter_height = 2, 3
        
        x = [x_pos, x_pos + counter_length, x_pos + counter_length, x_pos,
             x_pos, x_pos + counter_length, x_pos + counter_length, x_pos]
        y = [y_pos, y_pos, y_pos + counter_width, y_pos + counter_width,
             y_pos, y_pos, y_pos + counter_width, y_pos + counter_width]
        z = [height_offset + 0.5, height_offset + 0.5, height_offset + 0.5, height_offset + 0.5,
             height_offset + counter_height, height_offset + counter_height, 
             height_offset + counter_height, height_offset + counter_height]
        
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='#DAA520',
            opacity=0.8,
            name="Kitchen Counter",
            showlegend=False
        ))
    
    def _configure_3d_scene(self, fig: go.Figure, length: float, width: float, height: float):
        """Configure 3D scene with professional camera and lighting."""
        # Calculate optimal camera position
        max_dim = max(length, width, height)
        camera_distance = max_dim * 1.5
        
        fig.update_layout(
            title={
                'text': "Professional 3D Architectural Visualization",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2E86AB'}
            },
            scene=dict(
                xaxis=dict(
                    title="Length (feet)",
                    showgrid=True,
                    gridcolor='lightgray',
                    showline=True,
                    linecolor='gray'
                ),
                yaxis=dict(
                    title="Width (feet)",
                    showgrid=True,
                    gridcolor='lightgray',
                    showline=True,
                    linecolor='gray'
                ),
                zaxis=dict(
                    title="Height (feet)",
                    showgrid=True,
                    gridcolor='lightgray',
                    showline=True,
                    linecolor='gray'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=width/length, z=height/length),
                bgcolor='rgba(240, 248, 255, 0.8)'
            ),
            width=1000,
            height=700,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
    
    def _add_professional_lighting(self, fig: go.Figure):
        """Add professional lighting effects."""
        # This would be enhanced with more sophisticated lighting
        # For now, we rely on Plotly's default lighting with scene configuration
        pass
    
    def _export_interactive_html(self, fig: go.Figure, design: Optional[ArchitecturalDesign] = None,
                                title: str = "3D Architectural Visualization") -> str:
        """Export as interactive HTML."""
        # Add custom controls and information
        if design:
            building_info = f"""
            <div style="position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); 
                        padding: 10px; border-radius: 5px; font-family: Arial;">
                <h4>{design.input_parameters.bedroom_config} {design.input_parameters.building_type}</h4>
                <p><strong>Land Size:</strong> {design.input_parameters.land_size} sq.ft</p>
                <p><strong>Floors:</strong> {design.input_parameters.floors}</p>
                <p><strong>Facing:</strong> {design.input_parameters.facing}</p>
                <p><strong>Built Area:</strong> {design.space_efficiency.total_built_area:.0f} sq.ft</p>
            </div>
            """
        else:
            building_info = ""
        
        # Convert to HTML
        html_str = fig.to_html(
            include_plotlyjs='cdn',
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['pan3d', 'orbitRotation', 'tableRotation'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'architectural_3d_view',
                    'height': 700,
                    'width': 1000,
                    'scale': 2
                }
            }
        )
        
        # Add building info overlay
        html_str = html_str.replace('<body>', f'<body>{building_info}')
        
        # Encode to base64
        return base64.b64encode(html_str.encode()).decode()
    
    def _export_static_image(self, fig: go.Figure) -> str:
        """Export as static PNG image."""
        img_bytes = fig.to_image(format="png", width=1000, height=700, scale=2)
        return base64.b64encode(img_bytes).decode()
    
    def _export_for_download(self, fig: go.Figure, design: ArchitecturalDesign) -> Dict[str, str]:
        """Export multiple formats for download."""
        return {
            'html': self._export_interactive_html(fig, design),
            'png': self._export_static_image(fig),
            'json': fig.to_json()
        }
    
    def create_simple_3d_placeholder(self, design: ArchitecturalDesign) -> str:
        """Create a simple 3D placeholder when full rendering fails."""
        fig = go.Figure()
        
        # Create a simple building outline
        setbacks = design.setbacks
        land_side = design.input_parameters.land_size ** 0.5
        building_length = land_side - setbacks.front - setbacks.rear
        building_width = land_side - setbacks.left - setbacks.right
        building_height = design.input_parameters.floors * self.floor_height
        
        # Simple building box
        x = [0, building_length, building_length, 0, 0, building_length, building_length, 0]
        y = [0, 0, building_width, building_width, 0, 0, building_width, building_width]
        z = [0, 0, 0, 0, building_height, building_height, building_height, building_height]
        
        # Building faces
        i = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3]
        j = [1, 2, 3, 0, 5, 6, 7, 4, 4, 5, 6, 7]
        k = [2, 3, 0, 1, 6, 7, 4, 5, 1, 2, 3, 0]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='lightblue',
            opacity=0.7,
            name=f"{design.input_parameters.bedroom_config} Building",
            showlegend=True
        ))
        
        # Configure scene
        self._configure_3d_scene(fig, building_length, building_width, building_height)
        
        # Add title
        fig.update_layout(
            title=f"3D View - {design.input_parameters.bedroom_config} {design.input_parameters.building_type}",
            annotations=[
                dict(
                    text="Simplified 3D View<br>Full detailed view may be available after refresh",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=0.95, xanchor='center', yanchor='top',
                    font=dict(size=14, color="darkblue")
                )
            ]
        )
        
        return self._export_interactive_html(fig, design, "3D Building View")
    
    def create_virtual_walkthrough(self, design: ArchitecturalDesign,
                                 all_floor_plans: List[FloorPlan]) -> str:
        """Create virtual walkthrough with multiple camera angles."""
        # This would create an animated walkthrough
        # For now, return multiple static views
        views = []
        
        for angle in ['front', 'back', 'left', 'right', 'top', 'isometric']:
            fig = go.Figure()
            # Render building with specific camera angle
            # ... (implementation would be similar to render_3d_building)
            views.append(self._export_static_image(fig))
        
        return json.dumps(views)
