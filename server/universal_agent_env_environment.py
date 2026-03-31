import sys
import os
import random
import uuid
import json
import tempfile

# 💥 THE BULLETPROOF PATH
SHARED_FILE = os.path.join(tempfile.gettempdir(), "flood_data.json")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core import Environment
from models import UniversalAgentAction, UniversalAgentObservation, State

class UniversalAgentEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.world_state = self._generate_initial_state()

    def _generate_initial_state(self) -> State:
        return State(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            sector_levels=[0.2, 0.3, 0.2, 0.4, 0.1],
            active_rainfall=10.0,
            gates_open=[False, False, False, False, False]
        )

    def _write_state_to_file(self):
        state_data = {
            "levels": self.world_state.sector_levels,
            "rain": self.world_state.active_rainfall
        }
        try:
            with open(SHARED_FILE, "w") as f:
                json.dump(state_data, f)
        except Exception as e:
            print(f"Server Write Error: {e}")

    def reset(self, **kwargs) -> UniversalAgentObservation:
        print(f"\n🚨 BYPASS ONLINE - WRITING TO TEMP DIR 🚨\n")
        self.world_state = self._generate_initial_state()
        self._write_state_to_file()
        return UniversalAgentObservation(reward=0.0, done=False)

    def state(self) -> State:
        return self.world_state

    def step(self, action: UniversalAgentAction) -> UniversalAgentObservation:
        self.world_state.step_count += 1
        gate_idx = action.gate_id
        
        if 0 <= gate_idx < 5:
            if action.command == 'open':
                self.world_state.gates_open[gate_idx] = True
            elif action.command == 'close':
                self.world_state.gates_open[gate_idx] = False
        
        reward = 0.0
        done = False
        
        self.world_state.active_rainfall += random.uniform(-2.0, 5.0) 
        self.world_state.active_rainfall = max(0.0, min(50.0, self.world_state.active_rainfall))

        for i in range(5):
            self.world_state.sector_levels[i] += (self.world_state.active_rainfall / 100.0)
            
            if self.world_state.gates_open[i]:
                drain_rate = 0.1 + (action.pump_power * 0.05 if gate_idx == i else 0.0)
                self.world_state.sector_levels[i] -= drain_rate

            self.world_state.sector_levels[i] = max(0.0, min(1.0, self.world_state.sector_levels[i]))

            if self.world_state.sector_levels[i] >= 0.9:
                reward -= 10.0  
                done = True     
            elif self.world_state.sector_levels[i] > 0.7:
                reward -= 1.0   
            elif self.world_state.gates_open[i] and self.world_state.sector_levels[i] < 0.2:
                reward -= 0.5   
            else:
                reward += 0.5   

        if self.world_state.step_count >= 50:
            reward += 20.0 
            done = True

        self._write_state_to_file()
        return UniversalAgentObservation(reward=reward, done=done)