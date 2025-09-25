#!/usr/bin/env python3
"""
Demo script to showcase the enhanced professional blueprint generation capabilities.
This script generates sample designs to demonstrate the industry-ready features.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from architectural_engine import ArchitecturalDesigner
from visualization.cad_renderer import CADRenderer
from datetime import datetime

def create_sample_design():
    """Create a sample architectural design for demonstration."""
    
    # Sample input parameters for a 3BHK East-facing house
    sample_input = {
        'land_size': 2400.0,  # 2400 sq.ft plot
        'facing': 'East',
        'building_type': 'Independent House',
        'bedroom_config': '3BHK',
        'staircase_type': 'L-Shaped',
        'floors': 2,
        'budget_range': 'Medium',
        'special_requirements': ['Pooja Room', 'Study Room', 'Garden']
    }
    
    return sample_input

def generate_demo_blueprints():
    """Generate demonstration blueprints showcasing enhanced features."""
    
    print("Enhanced Blueprint Generation Demo")
    print("=" * 50)
    
    # Initialize components
    designer = ArchitecturalDesigner()
    cad_renderer = CADRenderer()
    
    # Create sample design
    print("\n1. Creating sample design...")
    sample_input = create_sample_design()
    design = designer.generate_design(sample_input)
    print(f"   OK: Generated design for {sample_input['bedroom_config']} {sample_input['building_type']}")
    
    # Generate all floor plans
    print("\n2. Generating floor plans...")
    all_floor_plans = designer.generate_all_floor_plans(design)
    print(f"   OK: Generated {len(all_floor_plans)} floor plans")
    
    # Create demo output directory
    demo_dir = current_dir / 'demo_output'
    demo_dir.mkdir(exist_ok=True)
    
    print(f"\n3. Rendering professional blueprints...")
    
    # Generate enhanced blueprints for each floor
    floor_names = ["Ground Floor", "First Floor", "Second Floor"]
    
    for i, floor_plan in enumerate(all_floor_plans):
        floor_name = floor_names[i] if i < len(floor_names) else f"Floor {i+1}"
        
        print(f"   Rendering {floor_name}...")
        
        # Generate professional blueprint with enhanced features
        title = f"Professional Architectural Floor Plan - {floor_name}"
        
        # Render with all enhanced features enabled
        blueprint_image = cad_renderer.render_floor_plan(
            floor_plan,
            title=title,
            show_dimensions=True,
            show_grid=True
        )
        
        # Save to demo directory
        output_file = demo_dir / f"{floor_name.lower().replace(' ', '_')}_blueprint.png"
        
        # Convert base64 to image file
        import base64
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(blueprint_image))
        
        print(f"   OK: Saved: {output_file}")
    
    # Generate summary report
    print(f"\n4. Creating demonstration summary...")
    
    summary_file = demo_dir / 'demo_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("Enhanced Blueprint Generation Demo Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Design Parameters:\n")
        f.write(f"- Plot Size: {sample_input['land_size']} sq.ft\n")
        f.write(f"- Orientation: {sample_input['facing']} facing\n")
        f.write(f"- Configuration: {sample_input['bedroom_config']}\n")
        f.write(f"- Building Type: {sample_input['building_type']}\n")
        f.write(f"- Floors: {sample_input['floors']}\n")
        f.write(f"- Staircase: {sample_input['staircase_type']}\n\n")
        
        f.write("Enhanced Features Demonstrated:\n")
        f.write("+ Professional architectural symbols (doors, windows, stairs)\n")
        f.write("+ Industry-standard title blocks with compass rose\n")
        f.write("+ Comprehensive dimension system with extension lines\n")
        f.write("+ Room-specific elements (bathroom fixtures, kitchen counters)\n")
        f.write("+ Proper wall thickness representation\n")
        f.write("+ Professional grid system (major/minor lines)\n")
        f.write("+ Vastu-compliant room positioning\n")
        f.write("+ Multi-floor layout generation\n")
        f.write("+ Detailed room labeling with areas\n")
        f.write("+ Construction-ready blueprint quality\n\n")
        
        f.write("Files Generated:\n")
        for i in range(len(all_floor_plans)):
            floor_name = floor_names[i] if i < len(floor_names) else f"Floor {i+1}"
            filename = f"{floor_name.lower().replace(' ', '_')}_blueprint.png"
            f.write(f"- {filename}\n")
    
    print(f"   OK: Summary saved: {summary_file}")
    
    print(f"\nDemo completed successfully!")
    print(f"Output directory: {demo_dir}")
    print(f"Files generated: {len(all_floor_plans)} blueprints + summary")
    
    print(f"\nKey Enhancements Showcased:")
    print(f"   + Professional architectural symbols and elements")
    print(f"   + Industry-standard title blocks and compass rose")
    print(f"   + Comprehensive dimensioning system")
    print(f"   + Construction-ready blueprint quality")
    print(f"   + Multi-floor layout generation")
    
    return demo_dir

if __name__ == "__main__":
    try:
        demo_dir = generate_demo_blueprints()
        
        print(f"\nTo view the enhanced blueprints:")
        print(f"   Navigate to: {demo_dir}")
        print(f"   Open the PNG files to see the professional quality")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
