import json
from architectural_engine.designer import ArchitecturalDesigner

designer = ArchitecturalDesigner()

def handler(event, context):
    try:
        design_data = json.loads(event['body'])
        design = designer.load_design_json(design_data)
        floor_plan = designer.generate_floor_plan(design)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(floor_plan.dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
