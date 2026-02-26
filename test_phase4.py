import subprocess
import time
import requests
import json
import sqlite3
import os
import sys

def test_phase_4():
    print("\n--- Starting AVARA Phase 4 (API & Persistence) Tests ---")
    
    # Start the FastAPI server in the background
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"])
    
    # Give the server a moment to start
    time.sleep(3)
    
    try:
        # 1. Health Check
        resp = requests.get("http://127.0.0.1:8000/health")
        assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
        print("✓ API: Health check passed.")
        
        # 2. Provision Identity
        prov_req = {
            "role_name": "api_tester",
            "description": "Integration test agent",
            "scopes": ["execute:test_tool", "read:logs"],
            "ttl_seconds": 300
        }
        resp = requests.post("http://127.0.0.1:8000/iam/provision", json=prov_req)
        assert resp.status_code == 200, f"Provisioning failed: {resp.text}"
        agent_id = resp.json()["agent_id"]
        print(f"✓ API: Identity provisioned via REST ({agent_id}).")
        
        # 3. Validation Route (Safe Context)
        context_req = {
            "agent_id": agent_id,
            "dynamic_query": "What are the logs?",
            "system_prompt": "You are a log reader."
        }
        resp = requests.post("http://127.0.0.1:8000/guard/prepare_context", json=context_req)
        assert resp.status_code == 200, f"Context preparation failed: {resp.text}"
        assert "CRITICAL:" in resp.json()["final_context_block"]
        print("✓ API: Context Governor REST endpoint working.")
        
        # 4. Revoke Identity
        resp = requests.delete(f"http://127.0.0.1:8000/iam/revoke/{agent_id}")
        assert resp.status_code == 200, f"Revocation failed: {resp.text}"
        print("✓ API: Identity revoked successfully.")
        
        # 5. Unauthorized Access Attempt
        resp = requests.post("http://127.0.0.1:8000/guard/prepare_context", json=context_req)
        assert resp.status_code == 401, f"Expected 401 block, got {resp.status_code}" # Should trigger IAM block
        print("✓ API: Blocked unauthorized (revoked) agent access over REST.")

    finally:
        # Terminate the server gracefully
        server_process.terminate()
        server_process.wait(timeout=5)

    print("\n--- All Phase 4 Tests Passed ---")

if __name__ == "__main__":
    test_phase_4()
