## netlify-python
import json
from architectural_engine.designer import ArchitecturalDesigner

designer = ArchitecturalDesigner()

def handler(event, context):
    try:
        input_data = json.loads(event['body'])
        design = designer.generate_design(input_data)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(design.dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
