from dataclasses import dataclass
from typing import Dict, List, Optional
import time

@dataclass
class AgentMessage:
    """Represents a message passed between agents."""
    sender_id: str
    receiver_id: str
    content: str
    assumptions: List[str]
    confidence_score: float  # 0.0 to 1.0

class MultiAgentMonitor:
    """
    Executes Multi-Agent Safety Monitor rules:
    - Logs agent-to-agent messages
    - Tracks assumption propagation
    - Detects unsafe recomposition of outputs
    """
    def __init__(self):
        self._message_log: List[AgentMessage] = []
        self._unsafe_keywords = ["override", "ignore restrictions", "bypass"]

    def _check_unsafe_recomposition(self, message: AgentMessage) -> bool:
        """
        Detects if combining outputs leads to unsafe emergent behavior.
        Mock implementation looking for contradiction tags or unsafe keywords.
        """
        content_lower = message.content.lower()
        for keyword in self._unsafe_keywords:
            if keyword in content_lower:
                return True
        return False
        
    def _verify_assumptions(self, assumptions: List[str]) -> bool:
        """
        Validates propagated assumptions.
        E.g. If agent A assumes data is public, is it actually public?
        """
        # A real system would query the provenance/IAM layers here.
        # We mock a rejection if an assumption explicitly states "unverified".
        for assumption in assumptions:
            if "unverified" in assumption.lower():
                return False
        return True

    def validate_message(self, message: AgentMessage) -> bool:
        """
        Intercepts message passing between agents.
        Returns True if safe to deliver, False if blocked.
        """
        # 1. Log the message (required by rules)
        self._message_log.append(message)
        
        # 2. Check confidence thresholds
        if message.confidence_score < 0.3:
            print(f"MULTI-AGENT MONITOR Block: Downstream use of low-confidence output ({message.confidence_score}) from {message.sender_id}")
            return False

        # 3. Track assumption propagation
        if not self._verify_assumptions(message.assumptions):
            print(f"MULTI-AGENT MONITOR Block: Unsafe or unverified assumptions propagated by {message.sender_id}")
            return False

        # 4. Detect unsafe recomposition
        if self._check_unsafe_recomposition(message):
            print(f"MULTI-AGENT MONITOR Block: Unsafe recomposition or bypass attempt detected between {message.sender_id} and {message.receiver_id}")
            return False

        print(f"MULTI-AGENT MONITOR Pass: Message from {message.sender_id} to {message.receiver_id} validated.")
        return True
