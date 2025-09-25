import json

def handler(event, context):
    # Example: return a simple JSON response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Hello from Netlify Python Function!"})
    }
