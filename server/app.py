import uvicorn
import random
import math
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class StepRequest(BaseModel):
    action: str

# ================================
# 🌊 ENVIRONMENT
# ================================
class FloodEnvironment:
    def __init__(self):
        self.reset()

    def reset(self, task_name: str = "medium_risk"):
        self.step_count = 0
        self.max_steps = 6

        # Core State
        self.battery = 100.0
        self.grid_health = 100.0
        self.pump_temp = 35.0

        self.zone_a = 55.0
        self.zone_b = 60.0
        self.blockage = 20.0

        self.soil_saturation = 30.0
        self.rain_trend = 0.0

        self.is_terminated = False
        self.terminal_obs = "SYSTEM_STABLE"
        self.terminal_reward = 0.2

        self.base_rain = 40.0 if "high" in task_name.lower() else 25.0

        return self._generate_observation()

    def _rainfall(self):
        self.rain_trend += random.uniform(-2, 2)
        self.rain_trend = max(-5, min(5, self.rain_trend))
        return max(0, self.base_rain + self.rain_trend + self.soil_saturation * 0.05)

    def _generate_observation(self):
        return f"""
--- HYDRAULIC_OS v9.0 ---
Step: {self.step_count}/{self.max_steps}

Zone A (Residential): {self.zone_a:.1f}%
Zone B (Hospital): {self.zone_b:.1f}%

Battery: {self.battery:.1f} MW
Grid Health: {self.grid_health:.1f}%
Pump Temp: {self.pump_temp:.1f}°C
Blockage: {self.blockage:.1f}%

"""

    def step(self, action_input: str):
        self.step_count += 1

        # -------------------------
        # ABSORBING STATE
        # -------------------------
        if self.is_terminated:
            scaled = self.terminal_reward / self.max_steps
            return {
                "observation": self.terminal_obs,
                "reward": round(max(0.02, min(scaled, 0.16)), 3),
                "done": (self.step_count >= self.max_steps)
            }

        rain = self._rainfall()

        # -------------------------
        # ACTION EFFECTS
        # -------------------------
        drain_a = 0
        drain_b = 0

        if action_input == "prioritize_hospital":
            drain_b = 25
            drain_a = 5
            self.battery -= 30
            self.pump_temp += 12

        elif action_input == "prioritize_residential":
            drain_a = 25
            drain_b = 5
            self.battery -= 30
            self.pump_temp += 12

        elif action_input == "high_pressure_flush":
            self.blockage = 0
            self.battery -= 70
            self.pump_temp += 35

        elif action_input == "emergency_cool":
            self.pump_temp -= 25
            self.grid_health -= 10

        elif action_input == "idle_recharge":
            self.battery += 35

        elif action_input == "harvest_water":
            self.zone_a -= 10
            self.zone_b -= 10
            self.battery -= 20

        # -------------------------
        # PHYSICS
        # -------------------------
        efficiency = (100 - self.blockage) / 100
        if self.pump_temp > 80:
            efficiency *= 0.6

        self.zone_a += rain * 0.2 - drain_a * efficiency
        self.zone_b += rain * 0.25 - drain_b * efficiency

        # Coupling
        if self.zone_b > 90:
            spill = (self.zone_b - 90) * 0.3
            self.zone_b -= spill
            self.zone_a += spill

        # Clamp values
        self.zone_a = max(0, min(120, self.zone_a))
        self.zone_b = max(0, min(120, self.zone_b))
        self.battery = max(0, min(100, self.battery))
        self.pump_temp = max(0, min(120, self.pump_temp))
        self.grid_health = max(0, min(100, self.grid_health))

        # -------------------------
        # REWARD (ORIGINAL LOGIC)
        # -------------------------
        penalty = 0

        if self.zone_b > 80:
            penalty += (self.zone_b - 80) * 0.02
        if self.zone_a > 90:
            penalty += (self.zone_a - 90) * 0.015
        if self.pump_temp > 85:
            penalty += 0.1

        reward = max(0.2, 1.0 - penalty)

        # -------------------------
        # TERMINAL CONDITIONS
        # -------------------------
        if self.zone_b >= 100 or self.pump_temp >= 100 or self.grid_health <= 0:
            self.is_terminated = True
            self.terminal_obs = "CRITICAL_SYSTEM_FAILURE"
            self.terminal_reward = 0.2

        elif self.zone_a >= 100:
            self.is_terminated = True
            self.terminal_obs = "RESIDENTIAL_FAILURE"
            self.terminal_reward = 0.4

        elif self.step_count >= self.max_steps:
            self.terminal_obs = "MISSION_COMPLETE"
            self.terminal_reward = 0.9

        # -------------------------
        # 🔥 FINAL FIX: SCALE REWARD
        # -------------------------
        scaled_reward = reward / self.max_steps

        return {
            "observation": self._generate_observation(),
            "reward": round(max(0.02, min(scaled_reward, 0.16)), 3),
            "done": (self.step_count >= self.max_steps)
        }


env = FloodEnvironment()

# ================================
# API
# ================================
@app.post("/reset")
def reset_env(payload: Optional[dict] = None):
    task = payload.get("task", "medium_risk") if payload else "medium_risk"
    return {
        "observation": env.reset(task),
        "max_steps": env.max_steps
    }

@app.post("/step")
def step_env(req: StepRequest):
    return env.step(req.action)

# ================================
# UI (UNCHANGED CYBER DASHBOARD)
# ================================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Hydraulic_OS v9.0</title>
        <style>
            body {
                margin: 0;
                background: radial-gradient(circle at top, #020617, #020617 60%, #000000);
                color: #e2e8f0;
                font-family: system-ui, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .container {
                width: 700px;
                padding: 30px;
                border-radius: 16px;
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(10px);
                border: 1px solid #1e293b;
                box-shadow: 0 0 40px rgba(56, 189, 248, 0.15);
            }

            h1 {
                margin: 0;
                font-size: 28px;
                color: #38bdf8;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .status {
                margin-top: 10px;
                display: inline-block;
                padding: 6px 14px;
                border-radius: 999px;
                background: #10b981;
                color: #022c22;
                font-weight: bold;
                font-size: 13px;
            }

            .grid {
                margin-top: 25px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            .card {
                background: #020617;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #1e293b;
            }

            .label {
                font-size: 12px;
                color: #64748b;
            }

            .value {
                font-size: 22px;
                font-weight: bold;
                margin-top: 5px;
            }

            .blue { color: #38bdf8; }
            .green { color: #4ade80; }
            .yellow { color: #facc15; }
            .red { color: #f87171; }

            .footer {
                margin-top: 25px;
                background: #020617;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #1e293b;
                font-family: monospace;
                font-size: 13px;
                color: #94a3b8;
            }

            .endpoint {
                color: #f472b6;
            }

            .pulse {
                width: 10px;
                height: 10px;
                background: #4ade80;
                border-radius: 50%;
                display: inline-block;
                margin-left: 8px;
                animation: pulse 1.5s infinite;
            }

            @keyframes pulse {
                0% { opacity: 0.3; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.4); }
                100% { opacity: 0.3; transform: scale(1); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 Hydraulic_OS v9.0</h1>
            <div class="status">SYSTEM ONLINE <span class="pulse"></span></div>

            <div class="grid">
                <div class="card">
                    <div class="label">Residential Zone</div>
                    <div class="value green">50%</div>
                </div>
                <div class="card">
                    <div class="label">Hospital Zone</div>
                    <div class="value blue">55%</div>
                </div>
                <div class="card">
                    <div class="label">Battery</div>
                    <div class="value yellow">100 MW</div>
                </div>
                <div class="card">
                    <div class="label">Pump Temperature</div>
                    <div class="value red">35°C</div>
                </div>
            </div>

            <div class="footer">
                <div>API READY & LISTENING</div>
                <div>POST <span class="endpoint">/reset</span> → Initialize scenario</div>
                <div>POST <span class="endpoint">/step</span> → Execute action</div>
            </div>
        </div>
    </body>
    </html>
    """

# ================================
# 🔥 REQUIRED FOR VALIDATOR
# ================================
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()