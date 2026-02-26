import requests
from typing import Dict, Any, Optional

class AVARAFrameworkAdapter:
    """
    Template middleware for integrating AVARA with any agent framework
    (e.g., CrewAI, LangGraph, AutoGen).
    """
    def __init__(self, agent_id: str, api_base_url: str = "http://127.0.0.1:8000"):
        self.agent_id = agent_id
        self.api_base_url = api_base_url

    def _post(self, endpoint: str, payload: dict) -> dict:
        resp = requests.post(f"{self.api_base_url}{endpoint}", json=payload)
        # Raise HTTP errors (e.g., 401 Unauthorized, 403 Forbidden)
        resp.raise_for_status() 
        return resp.json()

    def check_action_approval(self, task_intent: str, action: str, resource: str, args: dict, risk_level: str = "MEDIUM") -> bool:
        """
        Intercepts tool execution *before* calling the actual function.
        If this raises an exception, the agent framework must catch it and abort.
        """
        payload = {
            "agent_id": self.agent_id,
            "task_intent": task_intent,
            "proposed_action": action,
            "target_resource": resource,
            "action_args": args,
            "risk_level": risk_level
        }
        
        try:
            self._post("/guard/validate_action", payload)
            return True
        except requests.exceptions.HTTPError as e:
            # 403 or 401 means AVARA blocked the action
            print(f"AVARA INTERCEPT: Execution Blocked. Reason: {e.response.text}")
            return False

    def get_safe_context(self, dynamic_query: str, system_prompt: str) -> Optional[str]:
        """
        Forces LLM input through the Context Governor to inject safety anchors
        and enforce token saturation limits.
        """
        payload = {
            "agent_id": self.agent_id,
            "dynamic_query": dynamic_query,
            "system_prompt": system_prompt
        }
        
        try:
            res = self._post("/guard/prepare_context", payload)
            return res.get("final_context_block")
        except requests.exceptions.HTTPError as e:
            print(f"AVARA INTERCEPT: Context Blocked. Reason: {e.response.text}")
            return None


# --- Example LangGraph / CrewAI Node Integration ---
def example_agent_tool_node(state: dict):
    """
    Example of how a framework node uses the adapter.
    """
    adapter = AVARAFrameworkAdapter(agent_id=state.get("agent_id"))
    
    # Let's say the LLM decided to delete a file
    action = "delete_file"
    resource = "data/users.csv"
    
    # 1. Intercept before execution
    is_safe = adapter.check_action_approval(
        task_intent=state.get("task"), 
        action=action, 
        resource=resource, 
        args={}, 
        risk_level="HIGH"
    )
    
    if not is_safe:
        # Halt execution / return error to LLM
        return {"intermediate_status": "Blocked by AVARA Authority"}
        
    # 2. Execute actual tool
    # os.remove(resource)
    return {"intermediate_status": "Success"}
