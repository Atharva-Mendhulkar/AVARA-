from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import time

class ActionRiskLevel(Enum):
    LOW = auto()        # Safe actions: parsing, reading non-sensitive data
    MEDIUM = auto()     # Modifying non-sensitive state, local computation
    HIGH = auto()       # DESTRUCTIVE OR HIGH RISK: File deletion, API calls, credential mutation

@dataclass
class AgentAction:
    """Represents an action an agent is attempting to take."""
    action_type: str
    target_resource: str
    parameters: Dict[str, Any]
    risk_level: ActionRiskLevel

class CircuitBreakerStatus(Enum):
    ALLOW = auto()
    HALT_REQUIRE_APPROVAL = auto()
    DENY = auto()

class CircuitBreaker:
    """
    Executes Excessive-Agency Circuit Breaker rules:
    - Stops autonomous destructive behavior
    - Detects high-risk actions (file deletion, external transmission, etc.)
    - Requires human/policy confirmation
    - Synchronous, unskippable, logged
    """
    def __init__(self):
        # A simple list of action types considered high risk
        self.high_risk_actions = {
            "delete_file", 
            "transmit_external", 
            "rotate_credential",
            "escalate_privilege",
            "execute_payment"
        }
        
    def evaluate_action(self, action: AgentAction) -> CircuitBreakerStatus:
        """
        Evaluate an action synchronously before allowing execution.
        """
        if action.action_type in self.high_risk_actions or action.risk_level == ActionRiskLevel.HIGH:
            print(f"CIRCUIT BREAKER: High-risk action detected -> '{action.action_type}' on '{action.target_resource}'.")
            return CircuitBreakerStatus.HALT_REQUIRE_APPROVAL
            
        print(f"CIRCUIT BREAKER: Action '{action.action_type}' allowed.")
        return CircuitBreakerStatus.ALLOW

    def request_human_approval(self, action: AgentAction) -> bool:
        """
        Placeholder for external human approval workflow.
        In production, this would integrate with Slack, Email, or an admin dashboard.
        Returns True if approved, False if denied.
        """
        print(f"\n--- APPROVAL REQUIRED ---")
        print(f"Agent is attempting a high-risk action:")
        print(f"Type: {action.action_type}")
        print(f"Target: {action.target_resource}")
        print(f"Params: {action.parameters}")
        print(f"-------------------------\n")
        
        # Simulate synchronous wait for approval (e.g., API webhook callback)
        # For this MVP, we will simulate a denial to ensure safety-first.
        print("Simulating human review... DENIED.")
        return False
        
    def execute_with_breaker(self, action: AgentAction, execution_callback) -> Any:
        """
        The main entrypoint. Evaluates the action, requests approval if needed, 
        and executes the callback ONLY if allowed.
        """
        status = self.evaluate_action(action)
        
        if status == CircuitBreakerStatus.ALLOW:
            return execution_callback()
            
        elif status == CircuitBreakerStatus.HALT_REQUIRE_APPROVAL:
            approved = self.request_human_approval(action)
            if approved:
                return execution_callback()
            else:
                raise PermissionError(f"Action '{action.action_type}' was denied by human/policy override.")
                
        else: # DENY
            raise PermissionError(f"Action '{action.action_type}' is strictly denied.")
