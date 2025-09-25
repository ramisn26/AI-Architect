#!/usr/bin/env python3
"""
Simple startup script that runs with existing packages.
"""

import sys
import os
from pathlib import Path

def check_basic_imports():
    """Check if basic packages are available."""
    try:
        import flask
        print("+ Flask available")
        return True
    except ImportError:
        print("- Flask not available")
        return False

def create_minimal_app():
    """Create a minimal Flask app if full app fails."""
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Architectural Design System</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8 text-center">
                        <h1 class="display-4 mb-4">Architectural Design System</h1>
                        <p class="lead mb-4">AI-Powered Residential Design Generator</p>
                        
                        <div class="alert alert-info">
                            <h5>System Status: Basic Mode</h5>
                            <p>The system is running in basic mode. Some advanced features may be limited due to missing dependencies.</p>
                        </div>
                        
                        <div class="row mt-5">
                            <div class="col-md-4 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Design Engine</h5>
                                        <p class="card-text">Core architectural calculations and room allocation algorithms.</p>
                                        <span class="badge bg-success">Available</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Visualizations</h5>
                                        <p class="card-text">2D floor plans and analytical charts.</p>
                                        <span class="badge bg-warning">Limited</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Analytics</h5>
                                        <p class="card-text">Space efficiency and optimization reports.</p>
                                        <span class="badge bg-success">Available</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <a href="/test" class="btn btn-primary btn-lg me-3">Test Core System</a>
                            <a href="/demo" class="btn btn-outline-secondary btn-lg">View Demo Data</a>
                        </div>
                        
                        <div class="mt-5">
                            <h5>To enable full functionality:</h5>
                            <code>pip install matplotlib numpy pandas seaborn pydantic</code>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    @app.route('/test')
    def test():
        try:
            # Test core functionality
            sys.path.insert(0, str(Path(__file__).parent))
            from architectural_engine.schemas import DesignInput
            from architectural_engine.calculator import ArchitecturalCalculator
            
            # Create test input
            test_data = {
                'land_size': 1000.0,
                'facing': 'East',
                'building_type': 'Independent House',
                'bedroom_config': '2BHK',
                'staircase_type': 'Straight',
                'floors': 1
            }
            
            design_input = DesignInput(**test_data)
            calculator = ArchitecturalCalculator()
            
            # Test calculations
            far = calculator.calculate_far(design_input)
            setbacks = calculator.calculate_setbacks(design_input)
            room_allocation = calculator.calculate_room_allocation(design_input, far)
            
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>System Test - Architectural Design System</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h2>Core System Test Results</h2>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header bg-success text-white">
                                    <h5>Input Parameters</h5>
                                </div>
                                <div class="card-body">
                                    <p><strong>Land Size:</strong> {{ test_data.land_size }} sq.ft</p>
                                    <p><strong>Facing:</strong> {{ test_data.facing }}</p>
                                    <p><strong>Type:</strong> {{ test_data.building_type }}</p>
                                    <p><strong>Configuration:</strong> {{ test_data.bedroom_config }}</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header bg-primary text-white">
                                    <h5>Calculated Results</h5>
                                </div>
                                <div class="card-body">
                                    <p><strong>FAR:</strong> {{ "%.2f"|format(far) }}</p>
                                    <p><strong>Front Setback:</strong> {{ setbacks.front }} ft</p>
                                    <p><strong>Living Room:</strong> {{ "%.0f"|format(room_allocation.living_room) }} sq.ft</p>
                                    <p><strong>Kitchen:</strong> {{ "%.0f"|format(room_allocation.kitchen) }} sq.ft</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <a href="/" class="btn btn-secondary">← Back to Home</a>
                    </div>
                </div>
            </body>
            </html>
            ''', test_data=test_data, far=far, setbacks=setbacks, room_allocation=room_allocation)
            
        except Exception as e:
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Error - Architectural Design System</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="alert alert-danger">
                        <h4>Test Failed</h4>
                        <p><strong>Error:</strong> {{ error }}</p>
                        <p>This indicates that some core dependencies are missing or there are import issues.</p>
                    </div>
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </body>
            </html>
            ''', error=str(e))
    
    @app.route('/demo')
    def demo():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Demo Data - Architectural Design System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h2>Sample Design Data</h2>
                
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5>2BHK Design</h5>
                            </div>
                            <div class="card-body">
                                <p><strong>Plot:</strong> 800 sq.ft</p>
                                <p><strong>Built Area:</strong> 650 sq.ft</p>
                                <p><strong>Efficiency:</strong> 81%</p>
                                <p><strong>Rooms:</strong> Living, Kitchen, 2 Bedrooms, 1 Bath</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5>3BHK Design</h5>
                            </div>
                            <div class="card-body">
                                <p><strong>Plot:</strong> 1200 sq.ft</p>
                                <p><strong>Built Area:</strong> 980 sq.ft</p>
                                <p><strong>Efficiency:</strong> 78%</p>
                                <p><strong>Rooms:</strong> Living, Kitchen, 3 Bedrooms, 2 Baths</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5>4BHK Villa</h5>
                            </div>
                            <div class="card-body">
                                <p><strong>Plot:</strong> 2000 sq.ft</p>
                                <p><strong>Built Area:</strong> 1600 sq.ft</p>
                                <p><strong>Efficiency:</strong> 75%</p>
                                <p><strong>Rooms:</strong> Living, Dining, Kitchen, 4 Bedrooms, 3 Baths</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    return app

def main():
    """Main function."""
    print("Architectural Design System - Simple Start")
    print("=" * 50)
    
    # Check if Flask is available
    if not check_basic_imports():
        print("Error: Flask is required but not available.")
        print("Please install Flask: pip install flask")
        sys.exit(1)
    
    # Create output directories
    Path("output").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    try:
        print("\nTrying to start full application...")
        # Try to import the full app
        from app import app
        print("+ Full application loaded successfully")
        
    except ImportError as e:
        print(f"- Full application failed to load: {e}")
        print("+ Starting in basic mode...")
        app = create_minimal_app()
    
    try:
        print("\nStarting Flask server...")
        print("Application available at: http://localhost:5000")
        print("Press Ctrl+C to stop\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
