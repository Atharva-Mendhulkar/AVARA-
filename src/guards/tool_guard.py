from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import json

@dataclass
class ToolPermission:
    """Represents a permission required by a tool."""
    action: str
    resource: str
    description: str

@dataclass
class ToolRegistration:
    """
    Explicit registration of a tool within AVARA.
    Tools cannot self-describe their permissions; they must be registered.
    """
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    required_permissions: List[ToolPermission]
    is_active: bool = True

class ToolRegistry:
    """
    Manages the authoritative list of tools allowed by AVARA.
    Dynamic registration at runtime is forbidden by Rule 4.
    """
    def __init__(self):
        self._tools: Dict[str, ToolRegistration] = {}

    def register_tool(self, tool: ToolRegistration) -> None:
        """Register a new tool. Overwrites if exists."""
        self._tools[tool.name] = tool
        
    def get_tool(self, name: str) -> Optional[ToolRegistration]:
        """Retrieve a tool's registration by name."""
        return self._tools.get(name)
        
    def is_registered(self, name: str) -> bool:
        """Check if a tool is explicitly registered."""
        return name in self._tools and self._tools[name].is_active

class ToolGuard:
    """
    Executes Tool & MCP Execution Guard rules:
    - Explicit tool registration validation
    - Parameter schema validation
    - Permission checks before execution
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        
    def validate_invocation(self, tool_name: str, arguments: Dict[str, Any], agent_permissions: List[ToolPermission]) -> bool:
        """
        Validates if an agent can invoke a specific tool with given arguments.
        Returns True if allowed, raises exception or returns False if blocked.
        """
        # 1. Check if explicit registration exists
        tool_reg = self.registry.get_tool(tool_name)
        if not tool_reg:
            print(f"BLOCK: Tool '{tool_name}' is not registered.")
            return False
            
        # 2. Check if agent has all required permissions for this tool
        # In a real implementation this would check if agent_permissions cover required_permissions
        for required in tool_reg.required_permissions:
            has_permission = any(
                p.action == required.action and p.resource == required.resource 
                for p in agent_permissions
            )
            if not has_permission:
                 print(f"BLOCK: Agent lacks permission '{required.action}' on '{required.resource}' for tool '{tool_name}'.")
                 return False

        # 3. Parameter validation (Simplified for MVP, usually done with jsonschema)
        # Verify all provided arguments are defined in schema
        schema_props = tool_reg.parameters_schema.get("properties", {})
        for arg_name in arguments.keys():
            if arg_name not in schema_props:
                print(f"BLOCK: Unrecognized argument '{arg_name}' for tool '{tool_name}'. Metadata is untrusted.")
                return False

        # If we reach here, validation passed
        return True
