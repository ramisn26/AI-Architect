"""
Chart generator for space utilization analytics and reporting.
"""

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io
import base64

import sys
from pathlib import Path

# Add parent directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from architectural_engine.schemas import ArchitecturalDesign, RoomAllocation

class ChartGenerator:
    """Generates various charts and visualizations for space analysis."""
    
    def __init__(self):
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Color scheme
        self.colors = {
            'primary': '#3498DB',
            'secondary': '#E74C3C',
            'success': '#2ECC71',
            'warning': '#F39C12',
            'info': '#9B59B6',
            'light': '#ECF0F1',
            'dark': '#2C3E50'
        }
    
    def generate_space_allocation_pie_chart(self, design: ArchitecturalDesign) -> str:
        """Generate pie chart showing space allocation breakdown."""
        
        room_allocation = design.room_allocation
        
        # Prepare data
        categories = {
            'Living Areas': room_allocation.living_room,
            'Bedrooms': sum(room_allocation.bedrooms.values()),
            'Kitchen': room_allocation.kitchen,
            'Bathrooms': sum(room_allocation.bathrooms.values()),
            'Balcony': room_allocation.balcony,
            'Circulation': room_allocation.corridors,
            'Utility': room_allocation.utility,
            'Staircase': room_allocation.staircase
        }
        
        # Filter out zero values
        categories = {k: v for k, v in categories.items() if v > 0}
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(
            categories.values(), 
            labels=categories.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("husl", len(categories))
        )
        
        # Enhance appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Space Allocation Breakdown', fontsize=16, fontweight='bold', pad=20)
        
        # Add total area information
        total_area = sum(categories.values())
        ax.text(0, -1.3, f'Total Built Area: {total_area:.0f} sq.ft', 
               ha='center', fontsize=12, style='italic')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_room_comparison_chart(self, design: ArchitecturalDesign) -> str:
        """Generate bar chart comparing actual vs recommended room sizes."""
        
        room_allocation = design.room_allocation
        
        # Standard recommendations (from calculator)
        standards = {
            'Living Room': {'actual': room_allocation.living_room, 'recommended': 200},
            'Kitchen': {'actual': room_allocation.kitchen, 'recommended': 100},
            'Master Bedroom': {'actual': 0, 'recommended': 150},
            'Bathrooms': {'actual': sum(room_allocation.bathrooms.values()), 'recommended': 40}
        }
        
        # Add master bedroom actual value
        for name, area in room_allocation.bedrooms.items():
            if 'master' in name.lower():
                standards['Master Bedroom']['actual'] = area
                break
        
        # Prepare data for plotting
        rooms = list(standards.keys())
        actual_values = [standards[room]['actual'] for room in rooms]
        recommended_values = [standards[room]['recommended'] for room in rooms]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(rooms))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, actual_values, width, label='Actual', 
                      color=self.colors['primary'], alpha=0.8)
        bars2 = ax.bar(x + width/2, recommended_values, width, label='Recommended', 
                      color=self.colors['secondary'], alpha=0.8)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Room Types', fontsize=12, fontweight='bold')
        ax.set_ylabel('Area (sq.ft)', fontsize=12, fontweight='bold')
        ax.set_title('Actual vs Recommended Room Sizes', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(rooms)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_efficiency_dashboard(self, design: ArchitecturalDesign) -> str:
        """Generate comprehensive efficiency dashboard."""
        
        space_efficiency = design.space_efficiency
        
        # Create subplot layout
        fig = plt.figure(figsize=(15, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Efficiency Score Gauge
        ax1 = fig.add_subplot(gs[0, 0])
        self._create_gauge_chart(ax1, space_efficiency.utilization_score, 
                               "Utilization Score", "%")
        
        # 2. Carpet Area Ratio
        ax2 = fig.add_subplot(gs[0, 1])
        self._create_gauge_chart(ax2, space_efficiency.efficiency_ratio * 100, 
                               "Carpet Area Ratio", "%")
        
        # 3. Cost per sq.ft
        cost_per_sqft = design.total_cost_estimate / space_efficiency.total_built_area if design.total_cost_estimate else 0
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.text(0.5, 0.5, f'₹{cost_per_sqft:.0f}\nper sq.ft', 
                ha='center', va='center', fontsize=16, fontweight='bold',
                transform=ax3.transAxes)
        ax3.set_title('Construction Cost', fontweight='bold')
        ax3.axis('off')
        
        # 4. Space allocation pie chart (smaller version)
        ax4 = fig.add_subplot(gs[1, :2])
        room_allocation = design.room_allocation
        categories = {
            'Living': room_allocation.living_room,
            'Bedrooms': sum(room_allocation.bedrooms.values()),
            'Kitchen': room_allocation.kitchen,
            'Bathrooms': sum(room_allocation.bathrooms.values()),
            'Others': room_allocation.balcony + room_allocation.utility + room_allocation.corridors
        }
        categories = {k: v for k, v in categories.items() if v > 0}
        
        ax4.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%',
               colors=sns.color_palette("husl", len(categories)))
        ax4.set_title('Space Distribution', fontweight='bold')
        
        # 5. Recommendations text
        ax5 = fig.add_subplot(gs[1, 2])
        recommendations = space_efficiency.recommendations[:3]  # Top 3 recommendations
        rec_text = '\n\n'.join([f"• {rec}" for rec in recommendations])
        ax5.text(0.05, 0.95, 'Key Recommendations:\n\n' + rec_text, 
                transform=ax5.transAxes, fontsize=10, va='top', ha='left',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
        ax5.set_title('Optimization Tips', fontweight='bold')
        ax5.axis('off')
        
        # 6. Timeline and cost summary
        ax6 = fig.add_subplot(gs[2, :])
        summary_data = {
            'Total Area': f"{space_efficiency.total_built_area:.0f} sq.ft",
            'Carpet Area': f"{space_efficiency.carpet_area:.0f} sq.ft",
            'Efficiency': f"{space_efficiency.efficiency_ratio:.1%}",
            'Score': f"{space_efficiency.utilization_score:.0f}/100",
            'Timeline': design.timeline_estimate or "N/A",
            'Est. Cost': f"₹{design.total_cost_estimate/100000:.1f}L" if design.total_cost_estimate else "N/A"
        }
        
        # Create summary table
        table_data = [[k, v] for k, v in summary_data.items()]
        table = ax6.table(cellText=table_data, colLabels=['Parameter', 'Value'],
                         cellLoc='center', loc='center',
                         colWidths=[0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(summary_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#3498DB')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
        
        ax6.set_title('Project Summary', fontweight='bold', fontsize=14)
        ax6.axis('off')
        
        # Main title
        fig.suptitle('Architectural Design Analytics Dashboard', 
                    fontsize=18, fontweight='bold', y=0.95)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _create_gauge_chart(self, ax, value: float, title: str, unit: str):
        """Create a gauge chart for displaying metrics."""
        
        # Gauge parameters
        theta = np.linspace(0, np.pi, 100)
        
        # Background arc
        ax.plot(np.cos(theta), np.sin(theta), 'lightgray', linewidth=8)
        
        # Value arc
        value_theta = np.linspace(0, np.pi * (value / 100), int(value))
        
        # Color based on value
        if value >= 80:
            color = self.colors['success']
        elif value >= 60:
            color = self.colors['warning']
        else:
            color = self.colors['secondary']
        
        ax.plot(np.cos(value_theta), np.sin(value_theta), color, linewidth=8)
        
        # Center text
        ax.text(0, 0.1, f'{value:.1f}{unit}', ha='center', va='center', 
               fontsize=14, fontweight='bold')
        ax.text(0, -0.2, title, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.5, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
    
    def generate_cost_breakdown_chart(self, design: ArchitecturalDesign) -> str:
        """Generate cost breakdown chart."""
        
        if not design.total_cost_estimate:
            return ""
        
        # Estimated cost breakdown percentages
        cost_breakdown = {
            'Structure & Foundation': 0.35,
            'Walls & Roofing': 0.25,
            'Flooring & Finishing': 0.20,
            'Electrical & Plumbing': 0.15,
            'Miscellaneous': 0.05
        }
        
        total_cost = design.total_cost_estimate
        costs = {k: total_cost * v for k, v in cost_breakdown.items()}
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = list(costs.keys())
        values = list(costs.values())
        
        bars = ax.barh(categories, values, color=sns.color_palette("viridis", len(categories)))
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(value + total_cost * 0.01, bar.get_y() + bar.get_height()/2,
                   f'₹{value/100000:.1f}L', va='center', fontweight='bold')
        
        ax.set_xlabel('Cost (₹ Lakhs)', fontsize=12, fontweight='bold')
        ax.set_title(f'Estimated Cost Breakdown (Total: ₹{total_cost/100000:.1f}L)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
