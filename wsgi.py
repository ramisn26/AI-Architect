"""
WSGI entry point for production deployment.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the Flask app
from app import app

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Use environment variable for secret key in production
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

if __name__ == "__main__":
    # For local testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # For WSGI servers
    application = app
