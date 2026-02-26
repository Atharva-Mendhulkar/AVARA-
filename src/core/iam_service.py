import uuid
import time
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AgentRole:
    """Defines a role an agent operates under."""
    name: str
    description: str

@dataclass
class AgentIdentity:
    """
    Represents the strict identity of an autonomous agent:
    - ID, Role, Permission Scopes
    - Token TTL to prevent indefinite execution
    """
    agent_id: str
    role: AgentRole
    scopes: set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    token_ttl_seconds: int = 3600  # Default 1 hour

    def is_expired(self) -> bool:
        """Check if the agent's identity token has expired."""
        return (time.time() - self.created_at) > self.token_ttl_seconds

    def has_scope(self, required_scope: str) -> bool:
        return required_scope in self.scopes

class IAMService:
    """
    Manages Agent Identity & IAM lifecycle.
    - Agents cannot execute anonymously
    - Permissions are least-privilege
    - No implicit privilege chaining
    """
    def __init__(self):
        self._active_agents: dict[str, AgentIdentity] = {}

    def provision_identity(self, role: AgentRole, scopes: List[str], ttl: int = 3600) -> AgentIdentity:
        """Create a new ephemeral identity for an agent."""
        identity = AgentIdentity(
            agent_id=f"agt_{uuid.uuid4().hex[:8]}",
            role=role,
            scopes=set(scopes),
            token_ttl_seconds=ttl
        )
        self._active_agents[identity.agent_id] = identity
        print(f"IAM: Provisioned identity {identity.agent_id} with role '{role.name}'")
        return identity

    def validate_agent(self, agent_id: str) -> AgentIdentity:
        """
        Verify an agent exists and its token is valid.
        Raises PermissionError if unauthorized or expired.
        """
        if agent_id not in self._active_agents:
            raise PermissionError(f"IAM: Agent {agent_id} is not registered or anonymous.")

        identity = self._active_agents[agent_id]
        if identity.is_expired():
            self.revoke_identity(agent_id)
            raise PermissionError(f"IAM: Token expired for agent {agent_id}. Execution blocked.")

        return identity

    def revoke_identity(self, agent_id: str):
        """Revoke an agent's identity and halt further actions."""
        if agent_id in self._active_agents:
            del self._active_agents[agent_id]
            print(f"IAM: Revoked identity {agent_id}")
