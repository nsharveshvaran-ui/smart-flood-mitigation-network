import asyncio
import json
import os
import tempfile
from client import UniversalAgentEnv
from models import UniversalAgentAction

# 💥 THE BULLETPROOF PATH
SHARED_FILE = os.path.join(tempfile.gettempdir(), "flood_data.json")

def read_shared_state():
    try:
        with open(SHARED_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ AGENT READ ERROR: {e}") # Let's expose it if it fails!
        return {"levels": [0.0]*5, "rain": 0.0}

async def run_smart_agent():
    print("🌊 Connecting to the Smart Flood Mitigation Network...")
    env = UniversalAgentEnv(base_url="http://localhost:8000")
    
    await env.reset()
    
    # Read Initial State
    data = read_shared_state()
    water_levels = data.get("levels", [0.0]*5)
    
    print(f"Starting State: Water Levels: {[round(x, 2) for x in water_levels]} | Rainfall: {data.get('rain', 0.0):.2f} mm/hr")
    
    total_reward = 0.0
    done = False
    step_count = 0
    
    print("\n🚀 Beginning SMART Simulation Loop...\n")
    
    while not done and step_count < 50:
        
        data = read_shared_state()
        water_levels = data.get("levels", [0.0]*5)
        
        # Expert Logic
        max_water_level = max(water_levels)
        target_gate = water_levels.index(max_water_level)
        
        if max_water_level > 0.6:
            chosen_command = 'open'
            power = min(1.0, max_water_level + 0.2) 
        elif max_water_level < 0.2:
            chosen_command = 'close'
            power = 0.0
        else:
            chosen_command = 'open'
            power = 0.3
            
        action = UniversalAgentAction(
            message="Smart Mitigation Active",
            gate_id=target_gate,
            command=chosen_command,
            pump_power=power
        )
        
        step_result = await env.step(action)
        reward = step_result.reward
        done = step_result.done
        
        total_reward += reward
        step_count += 1
        
        print(f"Step {step_count:02d} | Target: Gate {target_gate} ({chosen_command.upper()}) | PUMP: {power:.2f} | Reward: {reward:5.2f} | Max Water: {max_water_level:.2f}")
        await asyncio.sleep(0.05) 
        
    print("\n=========================================")
    print(f"🏁 SIMULATION FINISHED")
    print(f"Total Steps Survived: {step_count}")
    print(f"Final SMART Agent Score: {total_reward:.2f}")
    print("=========================================\n")

if __name__ == "__main__":
    asyncio.run(run_smart_agent())