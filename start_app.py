#!/usr/bin/env python3
"""
Simple startup script for the Architectural Design System.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def install_missing_packages():
    """Install missing packages."""
    required_packages = [
        'flask',
        'numpy', 
        'pandas',
        'matplotlib',
        'seaborn',
        'pydantic',
        'pillow'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("Packages installed successfully!")
        except subprocess.CalledProcessError:
            print(f"Failed to install packages. Please run manually:")
            print(f"pip install {' '.join(missing)}")
            return False
    return True

def main():
    """Main function."""
    print("Architectural Design System - Starting...")
    print("=" * 50)
    
    # Install missing packages
    if not install_missing_packages():
        sys.exit(1)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    Path("static/output").mkdir(parents=True, exist_ok=True)
    
    try:
        print("\nStarting Flask application...")
        print("Application will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop the server\n")
        
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"Failed to import app: {e}")
        print("Make sure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
