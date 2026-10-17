from functools import wraps

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.schemas = {}
        self.descriptions = {}

    def tool(self,name=None,schema=None,description=None):
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name]=func
            self.schemas[tool_name]=schema or {}
            self.descriptions[tool_name]=description or func.__doc__ or ""

            @wraps
            def wrapper(*args,**kwargs):
                return func(*args,**kwargs)
            return wrapper
        return decorator
    
    def execute(self,action,params):
        if action not in self.tools:
            return {"error":f"Unknown Action : {action}"}
        return self.tools[action](**params)

    def list_tools(self):
        tool_list = []
        for tool_name, func in self.tools.items():
            tool_list.append({
                "name":tool_name,
                "description":self.descriptions.get(tool_name),
                "schema":self.schemas.get(tool_name)
            })
        return {"tools":tool_list}

    def get_tool_schema(self,name):
        if name not in self.schemas:
            return {"error":"Unknown Tool..."}
        return {
            "name":name,
            "schema":self.schemas[name],
            "description":self.descriptions.get(name,"")
        }


MCP = ToolRegistry()
