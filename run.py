#!/usr/bin/env python3
"""
Startup script for the Architectural Design System.
This script handles initialization, dependency checking, and app startup.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"OK: Python version: {sys.version}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'flask',
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'pydantic',
        'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"OK: {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"MISSING: {package}")
    
    if missing_packages:
        print(f"\nWARNING: Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("SUCCESS: All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install packages. Please run manually:")
            print(f"pip install {' '.join(missing_packages)}")
            sys.exit(1)

def setup_directories():
    """Create necessary directories."""
    directories = [
        'output',
        'static/output',
        'templates',
        'static/css',
        'static/js'
    ]
    
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"OK: Directory: {directory}")

def start_application():
    """Start the Flask application."""
    try:
        print("\nStarting Architectural Design System...")
        print("Application will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop the server\n")
        
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"ERROR: Failed to import app: {e}")
        print("Try installing missing dependencies:")
        print("   pip install flask matplotlib numpy pandas seaborn pydantic")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("Architectural Design System - Startup Script")
    print("=" * 50)
    
    # Step 1: Check Python version
    print("\n1. Checking Python version...")
    check_python_version()
    
    # Step 2: Setup directories
    print("\n2. Setting up directories...")
    setup_directories()
    
    # Step 3: Check dependencies
    print("\n3. Checking dependencies...")
    check_dependencies()
    
    # Step 4: Start application
    print("\n4. Starting application...")
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)