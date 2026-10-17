import json
import jsonschema
from config import SCHEMAS

def validate_json(action,data):
    """Validate JSON against schema for a specific action"""
    if action not in SCHEMAS:
        return False, f"No schema defined for action : {action}"
    try:
        jsonschema.validate(instance=data,schema=SCHEMAS[action])
        return True,None
    except jsonschema.ValidationError as e:
        return False,str(e)

