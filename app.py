"""
Main Flask web application for the Architectural Design System.
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
import os
import json
import zipfile
import tempfile
import base64
from datetime import datetime, timedelta
from typing import Dict, Any
from functools import wraps

# Fix matplotlib backend for web server environment
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from architectural_engine import ArchitecturalDesigner
from visualization.cad_renderer import CADRenderer
from visualization.renderer_3d import Renderer3D
from analytics.chart_generator import ChartGenerator

# Import authentication components
from models.user import user_manager, SubscriptionPlan
from auth.routes import auth_bp, login_required, get_current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'architectural_design_system_2024_secure_key_change_in_production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

# Make authentication functions available in all templates
@app.context_processor
def inject_user():
    return dict(get_current_user=get_current_user, now=datetime.now)

# Initialize components
designer = ArchitecturalDesigner()
cad_renderer = CADRenderer()
renderer_3d = Renderer3D()
chart_generator = ChartGenerator()

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def landing_page():
    """Landing page for non-authenticated users."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - redirect to auth blueprint."""
    return redirect(url_for('auth.dashboard'))

@app.route('/index')
@login_required
def index():
    """Main application page for authenticated users."""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    return render_template('index.html', user=user)

@app.route('/design', methods=['GET', 'POST'])
@login_required
def design_interface():
    """Design input interface with subscription checks."""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    # Check if user can create more designs
    if not user_manager.can_create_design(user):
        features = user_manager.get_plan_features(user.subscription_plan)
        flash(f'You have reached your monthly limit of {features.max_designs_per_month} designs. Please upgrade your plan to create more designs.', 'warning')
        return redirect(url_for('auth.subscription'))
    
    if request.method == 'POST':
        try:
            # Get form data
            input_data = {
                'land_size': float(request.form['land_size']),
                'facing': request.form['facing'],
                'building_type': request.form.get('building_type', 'Independent House'),  # Default to Independent House
                'bedroom_config': request.form['bedroom_config'],
                'staircase_type': request.form.get('staircase_type', 'Straight'),  # Default to Straight
                'floors': int(request.form.get('floors', 1)),
                'budget_range': request.form.get('budget_range'),
                'special_requirements': request.form.getlist('special_requirements')
            }
            
            # Generate design
            print("DEBUG: Generating design...")
            design = designer.generate_design(input_data)
            print("DEBUG: Design generated successfully")
            
            # Increment user's design count
            user_manager.increment_design_count(user.id)
            
            # Generate floor plan
            floor_plan = designer.generate_floor_plan(design)
            
            # Create project directory
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Use static/output for web-accessible files
            static_project_dir = os.path.join('static', 'output', project_id)
            os.makedirs(static_project_dir, exist_ok=True)
            
            # Also create in main output directory for data storage
            project_dir = os.path.join(OUTPUT_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Save design data
            design_file = os.path.join(project_dir, 'design.json')
            designer.export_design_json(design, design_file)
            
            # Generate all floor plans for multi-floor buildings
            print(f"DEBUG: Generating floor plans for {design.input_parameters.floors} floors")
            all_floor_plans = designer.generate_all_floor_plans(design)
            print(f"DEBUG: Generated {len(all_floor_plans)} floor plans")
            
            floor_plan_images = []
            
            # Generate blueprint for each floor
            floor_names = ["ground", "first", "second", "third"]
            for i, floor_plan in enumerate(all_floor_plans):
                floor_name = floor_names[i] if i < len(floor_names) else f"floor_{i+1}"
                title = f"Professional Floor Plan - {floor_name.title()} Floor"
                
                print(f"DEBUG: Rendering {floor_name} floor with {len(floor_plan.rooms)} rooms")
                
                floor_img = cad_renderer.render_floor_plan(
                    floor_plan, 
                    title=title,
                    show_dimensions=True,
                    show_grid=True
                )
                
                floor_plan_images.append({
                    'floor_number': i,
                    'floor_name': floor_name.title() + " Floor",
                    'image_data': floor_img,
                    'filename': f'{floor_name}_floor_plan.png'
                })
                
                print(f"DEBUG: {floor_name} floor image generated successfully")
            
            # Generate analytics
            space_chart = chart_generator.generate_space_allocation_pie_chart(design)
            efficiency_chart = chart_generator.generate_efficiency_dashboard(design)
            
            # Generate 3D visualization - Always ensure it's available
            print("DEBUG: Generating 3D visualization...")
            render_3d_html = None
            try:
                render_3d_html = renderer_3d.render_3d_building(design, all_floor_plans, 'interactive')
                print("DEBUG: 3D visualization generated successfully")
            except Exception as e:
                print(f"DEBUG: Full 3D building rendering failed: {e}")
                # Fallback: Try to generate 3D for just the ground floor
                try:
                    print("DEBUG: Attempting fallback 3D generation for ground floor...")
                    render_3d_html = renderer_3d.render_floor_3d(all_floor_plans[0], 0, True)
                    print("DEBUG: Fallback 3D visualization generated successfully")
                except Exception as e2:
                    print(f"DEBUG: Fallback 3D rendering also failed: {e2}")
                    # Last resort: Create a simple 3D placeholder
                    try:
                        print("DEBUG: Creating simple 3D placeholder...")
                        render_3d_html = renderer_3d.create_simple_3d_placeholder(design)
                        print("DEBUG: 3D placeholder created successfully")
                    except Exception as e3:
                        print(f"DEBUG: Even placeholder creation failed: {e3}")
                        render_3d_html = None
            
            # Save all floor plans
            floor_plan_paths = []
            print(f"DEBUG: Saving {len(floor_plan_images)} floor plan images to {static_project_dir}")
            
            for floor_data in floor_plan_images:
                filename = floor_data['filename']
                filepath = os.path.join(static_project_dir, filename)
                
                print(f"DEBUG: Saving {filename} to {filepath}")
                
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(floor_data['image_data']))
                
                # Verify file was saved
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"DEBUG: {filename} saved successfully ({file_size} bytes)")
                else:
                    print(f"ERROR: Failed to save {filename}")
                
                # Create web-accessible path
                web_path = f'/static/output/{project_id}/{filename}'
                floor_plan_paths.append({
                    'floor_name': floor_data['floor_name'],
                    'path': web_path,
                    'floor_number': floor_data['floor_number']
                })
            
            print(f"DEBUG: Created {len(floor_plan_paths)} floor plan paths")
            
            # Save main floor plan (ground floor) for compatibility
            if floor_plan_images:
                main_floor_path = os.path.join(static_project_dir, 'floor_plan.png')
                with open(main_floor_path, 'wb') as f:
                    f.write(base64.b64decode(floor_plan_images[0]['image_data']))
            
            # Save analytics charts
            space_chart_path = os.path.join(static_project_dir, 'space_allocation.png')
            with open(space_chart_path, 'wb') as f:
                f.write(base64.b64decode(space_chart))
            
            efficiency_chart_path = os.path.join(static_project_dir, 'efficiency_dashboard.png')
            with open(efficiency_chart_path, 'wb') as f:
                f.write(base64.b64decode(efficiency_chart))
            
            # Save 3D visualization - Always save something
            render_3d_path = os.path.join(static_project_dir, '3d_visualization.html')
            if render_3d_html:
                with open(render_3d_path, 'wb') as f:
                    f.write(base64.b64decode(render_3d_html))
                print(f"DEBUG: 3D visualization saved to {render_3d_path}")
            else:
                # Create a basic 3D unavailable message
                basic_3d_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>3D Visualization</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .message { background: #f0f8ff; padding: 30px; border-radius: 10px; margin: 20px; }
                        .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                    </style>
                </head>
                <body>
                    <div class="message">
                        <h2>3D Visualization</h2>
                        <p>3D view is being prepared for your design...</p>
                        <p>Please refresh the page or try generating a new design to see the 3D view.</p>
                        <button class="refresh-btn" onclick="window.location.reload()">Refresh Page</button>
                    </div>
                </body>
                </html>
                """
                with open(render_3d_path, 'w') as f:
                    f.write(basic_3d_html)
                print(f"DEBUG: Basic 3D placeholder saved to {render_3d_path}")
            
            # Create visualization paths
            visualizations = {
                'floor_plans': floor_plan_paths,  # Multiple floor plans
                'floor_plan': f'/static/output/{project_id}/floor_plan.png',  # Main floor plan
                'space_allocation': f'/static/output/{project_id}/space_allocation.png',
                'efficiency_dashboard': f'/static/output/{project_id}/efficiency_dashboard.png',
                'cost_breakdown': f'/static/output/{project_id}/cost_breakdown.png',
                '3d_visualization': f'/static/output/{project_id}/3d_visualization.html'  # Always available now
            }
            
            # Redirect to results page
            return redirect(url_for('view_results', project_id=project_id))
            
        except Exception as e:
            return render_template('design.html', error=str(e))
    
    return render_template('design.html')

@app.route('/results/<project_id>')
@login_required
def view_results(project_id):
    """View design results with feature restrictions."""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        project_dir = os.path.join(OUTPUT_DIR, project_id)
        
        # Load design data
        design_file = os.path.join(project_dir, 'design.json')
        design = designer.load_design_json(design_file)
        
        # Load visualization paths
        visualizations = {
            'floor_plans': [],
            'floor_plan': f'/static/output/{project_id}/floor_plan.png',
            'space_allocation': f'/static/output/{project_id}/space_allocation.png',
            'efficiency_dashboard': f'/static/output/{project_id}/efficiency_dashboard.png',
            'cost_breakdown': f'/static/output/{project_id}/cost_breakdown.png',
            '3d_visualization': f'/static/output/{project_id}/3d_visualization.html'
        }
        
        # Load floor plans from static directory
        static_project_dir = os.path.join('static', 'output', project_id)
        if os.path.exists(static_project_dir):
            for filename in os.listdir(static_project_dir):
                if filename.endswith('_floor_plan.png'):
                    floor_name = filename.split('_')[0].title() + " Floor"
                    floor_number = 0  # Default to ground floor
                    
                    # Determine floor number from filename
                    if filename.startswith('ground_'):
                        floor_number = 0
                    elif filename.startswith('first_'):
                        floor_number = 1
                    elif filename.startswith('second_'):
                        floor_number = 2
                    elif filename.startswith('third_'):
                        floor_number = 3
                    
                    visualizations['floor_plans'].append({
                        'floor_name': floor_name,
                        'path': f'/static/output/{project_id}/{filename}',
                        'floor_number': floor_number
                    })
            
            # Sort floor plans by floor number
            visualizations['floor_plans'].sort(key=lambda x: x['floor_number'])
        
        # Get user features for template
        features = user_manager.get_plan_features(user.subscription_plan)
        
        return render_template('results.html', 
                             design=design, 
                             visualizations=visualizations,
                             project_id=project_id,
                             user=user,
                             features=features)
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/generate_design', methods=['POST'])
def api_generate_design():
    """API endpoint for generating designs."""
    try:
        input_data = request.json
        design = designer.generate_design(input_data)
        return jsonify(design.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/generate_floor_plan', methods=['POST'])
def api_generate_floor_plan():
    """API endpoint for generating floor plans."""
    try:
        design_data = request.json
        design = designer.load_design_json(design_data)
        floor_plan = designer.generate_floor_plan(design)
        return jsonify(floor_plan.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download/<project_id>')
def download_project(project_id):
    """Download complete project as ZIP file."""
    try:
        project_dir = os.path.join(OUTPUT_DIR, project_id)
        
        # Create ZIP file
        zip_path = os.path.join(OUTPUT_DIR, f'{project_id}.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
        
        return send_file(zip_path, as_attachment=True, 
                        download_name=f'architectural_design_{project_id}.zip')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/gallery')
def gallery():
    """View gallery of generated designs."""
    projects = []
    
    if os.path.exists(OUTPUT_DIR):
        for project_folder in os.listdir(OUTPUT_DIR):
            if project_folder.startswith('project_'):
                project_path = os.path.join(OUTPUT_DIR, project_folder)
                design_file = os.path.join(project_path, 'design.json')
                
                if os.path.exists(design_file):
                    try:
                        design = designer.load_design_json(design_file)
                        projects.append({
                            'id': project_folder,
                            'design': design,
                            'thumbnail': f'/static/output/{project_folder}/floor_plan.png'
                        })
                    except:
                        continue
    
    return render_template('gallery.html', projects=projects)

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

def generate_all_visualizations(design, floor_plan, project_dir):
    """Generate all visualizations for a design."""
    visualizations = {}
    
    try:
        # 2D Floor Plan
        floor_plan_image = cad_renderer.render_floor_plan(
            floor_plan, 
            title="Architectural Floor Plan",
            output_path=os.path.join(project_dir, 'floor_plan.png')
        )
        visualizations['floor_plan'] = 'floor_plan.png'
        
        # Space Allocation Chart
        space_chart = chart_generator.generate_space_allocation_pie_chart(design)
        with open(os.path.join(project_dir, 'space_allocation.png'), 'wb') as f:
            f.write(base64.b64decode(space_chart))
        visualizations['space_allocation'] = 'space_allocation.png'
        
        # Efficiency Dashboard
        efficiency_chart = chart_generator.generate_efficiency_dashboard(design)
        with open(os.path.join(project_dir, 'efficiency_dashboard.png'), 'wb') as f:
            f.write(base64.b64decode(efficiency_chart))
        visualizations['efficiency_dashboard'] = 'efficiency_dashboard.png'
        
        # Cost Breakdown
        if design.total_cost_estimate:
            cost_chart = chart_generator.generate_cost_breakdown_chart(design)
            with open(os.path.join(project_dir, 'cost_breakdown.png'), 'wb') as f:
                f.write(base64.b64decode(cost_chart))
            visualizations['cost_breakdown'] = 'cost_breakdown.png'
        
        # Room Comparison Chart
        room_chart = chart_generator.generate_room_comparison_chart(design)
        with open(os.path.join(project_dir, 'room_comparison.png'), 'wb') as f:
            f.write(base64.b64decode(room_chart))
        visualizations['room_comparison'] = 'room_comparison.png'
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    
    return visualizations

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# Static file serving for output
@app.route('/static/output/<path:filename>')
def serve_output_file(filename):
    """Serve files from static/output directory."""
    static_output_dir = os.path.join(os.path.dirname(__file__), 'static', 'output')
    file_path = os.path.join(static_output_dir, filename)
    
    # Security check - ensure file is within static/output directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(static_output_dir)):
        return "Access denied", 403
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return f"File not found: {filename}", 404

if __name__ == '__main__':
    # Ensure all required directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
