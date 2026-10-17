import json, requests
from openai import OpenAI
from datetime import datetime
from config import (RPI_API_KEY,GENERATIVE_ENGINE_API_KEY_1,GENERATIVE_ENGINE_API_KEY_2,GENERATIVE_ENGINE_API_URL,RPI_API_URL)
import os

class GenerativeEngineClient:
    """
    MCP-Compliant LLM Client
    """

    def __init__(self,GEN_URL:str=GENERATIVE_ENGINE_API_URL,GEN_API:str=GENERATIVE_ENGINE_API_KEY_1) -> None:
        self.client = OpenAI(
            api_key=GEN_API,
            base_url=GEN_URL
        )
        self.tools = self._fetch_mcp_tools()
    
    def _fetch_mcp_tools(self):
        """Fetch available MCP Tools from RPI"""
        resp = requests.get(f"{RPI_API_URL}/mcp/tools",headers={"X-API-Key":RPI_API_KEY},timeout=5)
        resp.raise_for_status()
        return resp.json()["tools"]
        


    def process_command(self,user_prompt:str):
        """
        Convert User Prompt --> MCP action JSON
        NOTHING runs unless user expectily asks
        """
        base = os.path.dirname(__file__)
        path = os.path.join(base, "prompt.txt")
        with open(path,encoding="utf-8") as f:
            system_prompt = f.read()

        system_prompt = system_prompt.replace("&lt;LOCAL_VARIABLE&gt;", "<LOCAL_VARIABLE>")


        system_prompt = system_prompt.replace(
            "<LOCAL_VARIABLE>",
            json.dumps(self.tools, indent=2)
        ).strip() + "\n"

        completion = self.client.chat.completions.create(
            model="amazon.nova-lite-v1:0",
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt}
            ],
            temperature=0.1,
            max_tokens=512
        )
        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("LLM response content is None")
        raw = content.strip()

    # ---------------------------------------------------------------------
    #           Strict JSON PARSING 
    # ---------------------------------------------------------------------

        try:
            action_json = json.loads(raw)
        except json.JSONDecodeError:
            import re
            MATCH = re.search(r"\{.*\}",raw,re.DOTALL)
            if not MATCH:
                raise ValueError(f"LLM Returned Non- JSON : \n{raw}")
            action_json = json.loads(MATCH.group(0))

        with open("./logs/llm_response.log","a")as fd:
            fd.write(
                f"\n[{datetime.now()}]\n"
                f"USER : {user_prompt}\n"
                f"LLM : {json.dumps(action_json,indent=2)}\n"
            )
        return action_json
