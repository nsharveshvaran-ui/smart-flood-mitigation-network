import requests
import json

# This script acts as a baseline agent for the Flood Mitigation Network
URL = "http://localhost:8000"

def main():
    print("🌊 Starting Flood Mitigation Baseline Inference...")
    
    # 1. Reset the Environment
    print("\n[Action] Resetting Environment...")
    try:
        reset_resp = requests.post(f"{URL}/reset")
        print(f"[Response] {reset_resp.json()['observation']}")
    except Exception as e:
        print(f"Error: Could not connect to server. Ensure it's running at {URL}")
        return

    # 2. Execute a Step
    print("\n[Action] Sending Control Signal (Maintain Baseline)...")
    step_data = {"action": "monitor"}
    
    step_resp = requests.post(f"{URL}/step", json=step_data)
    result = step_resp.json()
    
    print(f"[Observation] {result['observation']}")
    print(f"[Reward] {result['reward']}")
    print(f"\n✅ Inference complete. System is stable.")

if __name__ == "__main__":
    main()