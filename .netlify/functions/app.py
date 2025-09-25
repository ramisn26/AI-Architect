"""
Netlify Functions handler for Flask app.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to Python path to import our Flask app
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Set matplotlib backend before importing app
import matplotlib
matplotlib.use('Agg')

try:
    from app import app
    
    def handler(event, context):
        """
        Netlify Functions handler for Flask app.
        """
        try:
            # Set up the environment
            os.environ['FLASK_ENV'] = 'production'
            app.config['ENV'] = 'production'
            app.config['DEBUG'] = False
            
            # Get the request details
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            query_string = event.get('queryStringParameters') or {}
            headers = event.get('headers', {})
            body = event.get('body', '')
            
            # Remove .netlify/functions/app from path if present
            if path.startswith('/.netlify/functions/app'):
                path = path.replace('/.netlify/functions/app', '') or '/'
            
            # Handle root path - keep as landing page (don't redirect to /index)
            if path == '/' or path == '':
                path = '/'
            
            # Create proper headers for Flask
            flask_headers = {}
            for key, value in headers.items():
                # Convert headers to proper format
                if key.lower() not in ['host', 'content-length']:
                    flask_headers[key] = value
            
            # Create a test client for the Flask app
            with app.test_client() as client:
                # Convert query parameters to query string
                query_str = '&'.join([f"{k}={v}" for k, v in query_string.items()])
                if query_str:
                    path = f"{path}?{query_str}"
                
                # Make the request based on HTTP method
                if http_method == 'GET':
                    response = client.get(path, headers=flask_headers)
                elif http_method == 'POST':
                    content_type = headers.get('content-type', 'application/x-www-form-urlencoded')
                    if 'application/json' in content_type:
                        response = client.post(path, json=json.loads(body) if body else {}, headers=flask_headers)
                    else:
                        response = client.post(path, data=body, headers=flask_headers)
                elif http_method == 'PUT':
                    response = client.put(path, data=body, headers=flask_headers)
                elif http_method == 'DELETE':
                    response = client.delete(path, headers=flask_headers)
                else:
                    response = client.get(path, headers=flask_headers)
                
                # Prepare response headers
                response_headers = {}
                for key, value in response.headers:
                    response_headers[key] = value
                
                # Add CORS headers for web compatibility
                response_headers.update({
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                })
                
                # Return the response
                return {
                    'statusCode': response.status_code,
                    'headers': response_headers,
                    'body': response.get_data(as_text=True)
                }
                
        except Exception as inner_e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Function execution error',
                    'message': str(inner_e),
                    'path': path,
                    'method': http_method
                })
            }

except Exception as e:
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Import error - Flask app could not be loaded',
                'message': str(e)
            })
        }
