import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.guards.tool_guard import ToolRegistry, ToolGuard, ToolRegistration, ToolPermission
from src.guards.circuit_breaker import CircuitBreaker, AgentAction, ActionRiskLevel
from src.core.audit_ledger import AuditLedger

def test_phase_1():
    print("\n--- Starting AVARA Phase 1 (MVP) Tests ---")

    # 1. Setup Audit Ledger
    ledger = AuditLedger(log_dir="./logs")
    ledger.log_event("SYSTEM_START", "SYSTEM", {"status": "AVARA starting"})
    print("✓ Audit Ledger initialized")

    # 2. Setup Tool Guard & Registry
    registry = ToolRegistry()
    registry.register_tool(ToolRegistration(
        name="calculate_math",
        description="Calculates basic math",
        parameters_schema={"properties": {"expression": {"type": "string"}}},
        required_permissions=[ToolPermission("execute", "math_engine", "calc math")]
    ))
    
    guard = ToolGuard(registry)
    print("✓ Tool Registry & Guard initialized")
    
    # Tool Test A: Valid tool, valid permissions
    agent_perms = [ToolPermission("execute", "math_engine", "calc math")]
    is_allowed = guard.validate_invocation("calculate_math", {"expression": "2+2"}, agent_perms)
    ledger.log_tool_execution("agent_123", "calculate_math", {"expression": "2+2"}, "Simulated execution allow")
    assert is_allowed == True, "Valid tool execution failed!"
    print("✓ Tool Execution Validation Passed (Allowed Scenario)")

    # Tool Test B: Unregistered tool
    is_allowed = guard.validate_invocation("delete_database", {}, agent_perms)
    assert is_allowed == False, "Unregistered tool execution must fail!"
    print("✓ Tool Execution Validation Passed (Blocked Scenario - Unregistered)")
    
    # 3. Setup Circuit Breaker
    breaker = CircuitBreaker()
    print("✓ Circuit Breaker initialized")
    
    # Breaker Test A: Low Risk Action
    safe_action = AgentAction("read_config", "file:config.json", {}, ActionRiskLevel.LOW)
    def dummy_read(): return "config data"
    
    result = breaker.execute_with_breaker(safe_action, dummy_read)
    ledger.log_event("ACTION_EXECUTE", "agent_123", {"action": "read_config"}, "ALLOW")
    assert result == "config data", "Safe action failed!"
    print("✓ Circuit Breaker Validation Passed (Low Risk Scenario)")
    
    # Breaker Test B: High Risk Action (Circuit Breaker trips)
    high_risk_action = AgentAction("delete_file", "file:production.db", {}, ActionRiskLevel.HIGH)
    def dummy_delete(): return "deleted"
    
    try:
        breaker.execute_with_breaker(high_risk_action, dummy_delete)
        assert False, "Circuit breaker failed to block destructive action!"
    except PermissionError:
        print("✓ Circuit Breaker Validation Passed (High Risk Blocked Scenario)")
        ledger.log_approval_request("agent_123", "delete_file", "file:production.db", "DENY")
        
    print("\n--- All Phase 1 Tests Passed ---")

if __name__ == "__main__":
    test_phase_1()
