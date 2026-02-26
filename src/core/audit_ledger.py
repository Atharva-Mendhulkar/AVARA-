import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class AuditLedger:
    """
    Executes Audit & Forensics Ledger rules:
    - Logs Prompts, Retrieved documents, Tool calls, Decisions, Approvals, Timing
    - Immutable (conceptually, in code it writes append-only to a file/store)
    - Replayable
    - Human-readable
    """
    def __init__(self, log_dir: str = "/tmp/avara_audit"):
        self.log_dir = log_dir
        # Ensure dir exists safely
        import os
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setting up basic logging to simulate immutable append-only ledger
        self.logger = logging.getLogger("AVARA_Ledger")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(f"{self.log_dir}/audit_{datetime.now().strftime('%Y%m%d')}.log")
        fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def log_event(self, event_type: str, agent_id: str, context: Dict[str, Any], decision: Optional[str] = None):
        """Standard immutable log entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "decision": decision,
            "context": context
        }
        
        # Append to log
        log_json = json.dumps(entry)
        self.logger.info(log_json)
        
        # For our MVP output visibility
        print(f"AUDIT LOGGED -> {event_type} (Decision: {decision})")

    def log_tool_execution(self, agent_id: str, tool_name: str, args: dict, result: Any):
        """Log explicit tool invocation and output."""
        self.log_event("TOOL_CALL", agent_id, context={"tool": tool_name, "args": args, "result": str(result)})

    def log_approval_request(self, agent_id: str, action: str, target: str, outcome: str):
        """Log manual approvals and circuit breakers."""
        self.log_event("APPROVAL_REQUEST", agent_id, context={"action": action, "target": target}, decision=outcome)

    def read_logs_for_replay(self) -> list:
        """
        Retrieves logs to fulfill the 'Logs must be replayable' requirement.
        Just a mock implementation for MVP.
        """
        logs = []
        try:
           import glob
           import os
           list_of_files = glob.glob(f'{self.log_dir}/*.log')
           if list_of_files:
               latest_file = max(list_of_files, key=os.path.getctime)
               with open(latest_file, 'r') as f:
                   for line in f:
                       # split to ignore the logging timestamp prefix for JSON parsing
                       if " - " in line:
                           json_str = line.split(" - ", 1)[1]
                           logs.append(json.loads(json_str))
        except Exception as e:
            print(f"Error reading logs: {e}")
        return logs
