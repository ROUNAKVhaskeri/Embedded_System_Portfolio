from flask import Flask, request, jsonify,Response
import time,json,threading,os,logging

from config import API_HOST,API_KEY,API_PORT,logger
from Mcp.tools_registry import MCP 
from Mcp.json_validator import validate_json

import Mcp.hardware_api

# ------------------------------------------------
#       LOGGING
# ------------------------------------------------


# ------------------------------------------------
#       FLASK APP
# ------------------------------------------------
app = Flask(__name__)

# ------------------------------------------------
#       API: Execute MCP Tool
# ------------------------------------------------

@app.route("/api/execute",methods=["POST"])
def execute_action():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error":"Unauthorized"}),401
    if not request.is_json:
        return jsonify({"error":"Content-Type must be application/json"}),415
    
    payload = request.json
    if "action" not in payload or "params" not in payload:
        return jsonify({"error":"Invalid Request Format.."}),400
    print(f"Received POST : \n{payload}")
    
    action = payload["action"]
    params = payload["params"]

    is_valid, error = validate_json(action,params)
    if not is_valid:
        return jsonify({"Error":f"Invalid Parameters : {error}"}),400
    result = MCP.execute(action,params)
    return jsonify(result)


    
# ------------------------------------------------
#       MCP Discovery Endpoint
# ------------------------------------------------

@app.route("/api/mcp/tools",methods=["GET"])
def list_mcp_tools():
    return jsonify(MCP.list_tools())

@app.route("/api/mcp/schema/<tool_name>",methods=["GET"])
def get_mcp_schema(tool_name):
    return jsonify(MCP.get_tool_schema(tool_name))


# ------------------------------------------------
#       HEALTH / STATUS
# ------------------------------------------------
@app.route("/api/status",methods=["GET"])
def status():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error":"Unauthorized"}),401
    return jsonify({
        "status":"running",
        "uptime":time.time(),
        "hostname":os.uname()[1]
    })


if __name__ == '__main__':
    logger.info("Starting RPI MCP Flask Server")
    app.run(host=API_HOST,port=API_PORT,threaded=True)