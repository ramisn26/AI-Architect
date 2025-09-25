"""
Space analysis module for architectural designs.
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

import sys
from pathlib import Path

# Add parent directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from architectural_engine.schemas import ArchitecturalDesign, RoomAllocation

class SpaceAnalyzer:
    """Analyzes space utilization and efficiency in architectural designs."""
    
    def __init__(self):
        # Standard space efficiency benchmarks
        self.efficiency_benchmarks = {
            'excellent': 0.85,
            'good': 0.75,
            'average': 0.65,
            'poor': 0.55
        }
        
        # Room type categories for analysis
        self.room_categories = {
            'living_spaces': ['living_room', 'family_room', 'dining_room'],
            'private_spaces': ['bedroom', 'master_bedroom', 'study'],
            'service_spaces': ['kitchen', 'utility', 'storage'],
            'hygiene_spaces': ['bathroom', 'toilet', 'washroom'],
            'circulation': ['corridor', 'hallway', 'staircase'],
            'outdoor': ['balcony', 'terrace', 'garden']
        }
    
    def analyze_space_distribution(self, design: ArchitecturalDesign) -> Dict:
        """Analyze the distribution of space across different categories."""
        
        room_allocation = design.room_allocation
        
        # Calculate areas by category
        category_areas = {}
        
        # Living spaces
        living_area = room_allocation.living_room
        category_areas['living_spaces'] = living_area
        
        # Private spaces (bedrooms)
        private_area = sum(room_allocation.bedrooms.values())
        category_areas['private_spaces'] = private_area
        
        # Service spaces
        service_area = room_allocation.kitchen + room_allocation.utility
        category_areas['service_spaces'] = service_area
        
        # Hygiene spaces
        hygiene_area = sum(room_allocation.bathrooms.values())
        category_areas['hygiene_spaces'] = hygiene_area
        
        # Circulation
        circulation_area = room_allocation.corridors + room_allocation.staircase
        category_areas['circulation'] = circulation_area
        
        # Outdoor spaces
        outdoor_area = room_allocation.balcony
        category_areas['outdoor'] = outdoor_area
        
        # Calculate total and percentages
        total_area = sum(category_areas.values())
        category_percentages = {
            category: (area / total_area * 100) if total_area > 0 else 0
            for category, area in category_areas.items()
        }
        
        return {
            'areas': category_areas,
            'percentages': category_percentages,
            'total_area': total_area
        }
    
    def calculate_efficiency_metrics(self, design: ArchitecturalDesign) -> Dict:
        """Calculate various efficiency metrics."""
        
        space_efficiency = design.space_efficiency
        room_allocation = design.room_allocation
        
        # Carpet area efficiency
        carpet_efficiency = space_efficiency.efficiency_ratio
        
        # Circulation efficiency (should be 10-15% ideally)
        total_usable = space_efficiency.carpet_area
        circulation_ratio = room_allocation.corridors / total_usable if total_usable > 0 else 0
        
        # Room size efficiency (how well rooms match standards)
        room_efficiency = self._calculate_room_size_efficiency(room_allocation)
        
        # Overall space utilization
        utilization_score = space_efficiency.utilization_score
        
        return {
            'carpet_efficiency': carpet_efficiency,
            'circulation_efficiency': circulation_ratio,
            'room_size_efficiency': room_efficiency,
            'overall_utilization': utilization_score / 100,
            'efficiency_grade': self._get_efficiency_grade(utilization_score)
        }
    
    def compare_with_standards(self, design: ArchitecturalDesign) -> Dict:
        """Compare design with industry standards."""
        
        room_allocation = design.room_allocation
        input_params = design.input_parameters
        
        # Standard room sizes (sq.ft)
        standards = {
            'living_room': {'min': 120, 'ideal': 200, 'max': 350},
            'master_bedroom': {'min': 120, 'ideal': 150, 'max': 200},
            'bedroom': {'min': 80, 'ideal': 120, 'max': 150},
            'kitchen': {'min': 60, 'ideal': 100, 'max': 150},
            'bathroom': {'min': 25, 'ideal': 40, 'max': 60}
        }
        
        comparisons = {}
        
        # Living room comparison
        living_area = room_allocation.living_room
        living_std = standards['living_room']
        comparisons['living_room'] = self._compare_room_size(living_area, living_std)
        
        # Kitchen comparison
        kitchen_area = room_allocation.kitchen
        kitchen_std = standards['kitchen']
        comparisons['kitchen'] = self._compare_room_size(kitchen_area, kitchen_std)
        
        # Bedroom comparisons
        for bedroom_name, area in room_allocation.bedrooms.items():
            if 'master' in bedroom_name.lower():
                std = standards['master_bedroom']
            else:
                std = standards['bedroom']
            comparisons[bedroom_name] = self._compare_room_size(area, std)
        
        # Bathroom comparisons
        avg_bathroom_area = sum(room_allocation.bathrooms.values()) / len(room_allocation.bathrooms)
        bathroom_std = standards['bathroom']
        comparisons['average_bathroom'] = self._compare_room_size(avg_bathroom_area, bathroom_std)
        
        return comparisons
    
    def generate_optimization_suggestions(self, design: ArchitecturalDesign) -> List[str]:
        """Generate specific optimization suggestions."""
        
        suggestions = []
        
        # Analyze space distribution
        distribution = self.analyze_space_distribution(design)
        percentages = distribution['percentages']
        
        # Check circulation space
        if percentages.get('circulation', 0) > 20:
            suggestions.append("Reduce circulation space by optimizing corridor widths and layout")
        elif percentages.get('circulation', 0) < 8:
            suggestions.append("Increase circulation space for better movement flow")
        
        # Check living space proportion
        if percentages.get('living_spaces', 0) < 25:
            suggestions.append("Consider increasing living room size for better social interaction")
        elif percentages.get('living_spaces', 0) > 40:
            suggestions.append("Living space is oversized - consider adding dining area or study")
        
        # Check service space proportion
        if percentages.get('service_spaces', 0) < 10:
            suggestions.append("Kitchen and utility areas may be undersized")
        elif percentages.get('service_spaces', 0) > 20:
            suggestions.append("Service areas are oversized - optimize kitchen layout")
        
        # Check outdoor space
        if percentages.get('outdoor', 0) < 5:
            suggestions.append("Consider adding balcony or terrace for outdoor access")
        
        # Efficiency-based suggestions
        efficiency_metrics = self.calculate_efficiency_metrics(design)
        
        if efficiency_metrics['carpet_efficiency'] < 0.65:
            suggestions.append("Improve carpet area ratio by reducing wall thickness or optimizing layout")
        
        if efficiency_metrics['room_size_efficiency'] < 0.7:
            suggestions.append("Adjust room sizes to better match functional requirements")
        
        # Standards-based suggestions
        comparisons = self.compare_with_standards(design)
        
        for room, comparison in comparisons.items():
            if comparison['status'] == 'undersized':
                suggestions.append(f"{room.replace('_', ' ').title()} is undersized - consider expanding")
            elif comparison['status'] == 'oversized':
                suggestions.append(f"{room.replace('_', ' ').title()} is oversized - space could be better utilized")
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def _calculate_room_size_efficiency(self, room_allocation: RoomAllocation) -> float:
        """Calculate how efficiently room sizes match standards."""
        
        standards = {
            'living_room': {'ideal': 200},
            'kitchen': {'ideal': 100},
            'master_bedroom': {'ideal': 150},
            'bedroom': {'ideal': 120},
            'bathroom': {'ideal': 40}
        }
        
        efficiency_scores = []
        
        # Living room
        living_score = min(room_allocation.living_room / standards['living_room']['ideal'], 1.0)
        efficiency_scores.append(living_score)
        
        # Kitchen
        kitchen_score = min(room_allocation.kitchen / standards['kitchen']['ideal'], 1.0)
        efficiency_scores.append(kitchen_score)
        
        # Bedrooms
        for bedroom_name, area in room_allocation.bedrooms.items():
            if 'master' in bedroom_name.lower():
                ideal = standards['master_bedroom']['ideal']
            else:
                ideal = standards['bedroom']['ideal']
            score = min(area / ideal, 1.0)
            efficiency_scores.append(score)
        
        # Bathrooms
        if room_allocation.bathrooms:
            avg_bathroom = sum(room_allocation.bathrooms.values()) / len(room_allocation.bathrooms)
            bathroom_score = min(avg_bathroom / standards['bathroom']['ideal'], 1.0)
            efficiency_scores.append(bathroom_score)
        
        return sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0
    
    def _compare_room_size(self, actual_area: float, standard: Dict) -> Dict:
        """Compare actual room size with standards."""
        
        if actual_area < standard['min']:
            status = 'undersized'
            deviation = (standard['min'] - actual_area) / standard['min'] * 100
        elif actual_area > standard['max']:
            status = 'oversized'
            deviation = (actual_area - standard['max']) / standard['max'] * 100
        else:
            status = 'optimal'
            deviation = abs(actual_area - standard['ideal']) / standard['ideal'] * 100
        
        return {
            'actual': actual_area,
            'standard': standard,
            'status': status,
            'deviation_percent': deviation
        }
    
    def _get_efficiency_grade(self, score: float) -> str:
        """Get efficiency grade based on score."""
        
        if score >= 85:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
