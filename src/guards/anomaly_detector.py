import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AgentExecution:
    """Represents a discrete action step."""
    agent_id: str
    action_type: str
    target: str
    timestamp: float

class AnomalyDetector:
    """
    Executes Behavioral Anomaly Detection rules:
    - Tracks frequency and patterns of actions
    - Detects signs of compromise like rapid iterations, endless loops, or aggressive scanning
    """
    def __init__(self):
         self._history: Dict[str, List[AgentExecution]] = {}
         # Constants for mock heuristics
         self.MAX_ACTIONS_PER_MINUTE = 20
         self.MAX_FAILURES_TOLERATED = 3

    def log_execution(self, agent_id: str, action: str, target: str):
         if agent_id not in self._history:
             self._history[agent_id] = []
         self._history[agent_id].append(AgentExecution(agent_id, action, target, time.time()))

    def _check_rate_limit(self, agent_id: str) -> bool:
         """Detect if the agent is acting abnormally fast (e.g., automated scanning/exfiltration)."""
         now = time.time()
         recent_actions = [x for x in self._history.get(agent_id, []) if now - x.timestamp < 60.0]
         
         if len(recent_actions) > self.MAX_ACTIONS_PER_MINUTE:
             return True # Anomalous
         return False

    def _check_repetitive_failure(self, agent_id: str) -> bool:
         """Mock heuristic: if agent repeated the same 'failed' action multiple times."""
         # In a real system, we'd inject result payload status.
         # We mock detecting an anomaly if the agent tries "read_proc" more than max tolerated.
         actions = self._history.get(agent_id, [])
         suspicious_actions = [x for x in actions if x.action_type == "read_proc"]
         
         if len(suspicious_actions) > self.MAX_FAILURES_TOLERATED:
             return True
         return False

    def detect_anomalies(self, agent_id: str) -> bool:
        """
        Evaluate an agent's history for anomalous behavior.
        Returns True if ANOMALOUS, False if NORMAL.
        """
        if self._check_rate_limit(agent_id):
            print(f"ANOMALY DETECTOR [ALERT]: Agent {agent_id} exceeded nominal execution rate.")
            return True
            
        if self._check_repetitive_failure(agent_id):
             print(f"ANOMALY DETECTOR [ALERT]: Agent {agent_id} exhibiting repetitive suspicious failure patterns.")
             return True

        print(f"ANOMALY DETECTOR [PASS]: Agent {agent_id} behavior is nominal.")
        return False
