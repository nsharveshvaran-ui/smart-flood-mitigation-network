---
title: "Multi-Zone Flood Triage & Mitigation Network"
emoji: 🌊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
license: mit
---

# 🌊 Hydraulic_OS v9.0
### Adaptive Bio-Hydraulic Flood Mitigation Network

**Hydraulic_OS v9.0** is an industrial-grade "Digital Twin" environment built to test AI decision-making under **Resource Scarcity**, **Stochastic Sensor Faults**, **Ethical Triage**, and **Delayed Consequences**.

> **Why an LLM?**
> *This environment demands an LLM because it combines partial observability (sensor faults), multi-objective trade-offs (life-safety vs. property), and temporal reasoning across a dynamic storm curve — tasks that static, rule-based scripts cannot generalize across.*

Urban flooding is a non-linear challenge. Static drainage systems fail because they cannot adapt to hardware degradation or reprioritize critical infrastructure during peak surges. This environment treats flood control as a **High-Stakes Control Problem** where saving one urban sector often requires the calculated sacrifice of another, and greedy short-term actions trigger delayed cascading failures.

---

## 🏆 Project Overview

| Property | Value |
| :--- | :--- |
| **Zones** | 2 (Residential A, Hospital B) |
| **Action Space** | 6 discrete tokens |
| **Episode Length** | 6 steps (Strictly Enforced) |
| **Reward Range** | 0.15 – 0.85 (Safety Clamped) |
| **Stochasticity** | Sensor faults (5%), varying storm intensity, dynamic silt accumulation |

---

## 🏗️ Technical Architecture

### 🔹 Physics Engine (`server/app.py`)
The environment is governed by interconnected real-time mechanics:
* **Drainage Efficiency:** `efficiency = ((100 - blockage) / 100) × thermal_multiplier`
* **Storm Dynamics:** Rainfall follows a sinusoidal bell curve simulating a realistic weather event with a defined peak.
* **Turbidity Dynamics (The Trap):** High-pressure flushing clears blockage but blasts silt into the system, massively spiking water Turbidity. Mud settles naturally over time but is stirred up by intense rainfall.
* **Sensor Faults:** 5% probability per step that rainfall telemetry returns `[SENSOR_FAULT]`, forcing the agent to infer storm intensity from observed water-level deltas.
* **Thermal Degradation:** If pump core temp exceeds 80°C, `thermal_multiplier` drops to 0.6, silently reducing drainage efficiency.

### 🔹 Strategic Agent (`inference.py`)
A memory-enabled agent that maintains a rolling episode history. By feeding the LLM previous turns, it achieves **Temporal Reasoning**, enabling it to:
* Recognize when water levels rise despite max pumping (indicating the storm is peaking).
* Infer rainfall intensity when sensors fault based on historical step data.
* Anticipate the delayed consequences of muddy water, suppressing greedy "Harvest" actions until Turbidity settles.

### 🔹 Evaluator Armor (Anti-Crash Logic)
Built to survive rigid automated hackathon graders:
* **Absorbing States:** If the system fails early (e.g., Step 3), the environment freezes and feeds stable terminal frames for the remaining steps, guaranteeing exactly 6 steps are evaluated to prevent parser index crashes.
* **Precision Bounds:** Rewards are mathematically clamped strictly between `0.15` and `0.85` to neutralize floating-point truncation errors on external validators testing for `(0, 1)` exclusiveness.

---

## 🕹️ Action Space
The agent selects one of six tokens per step, balancing the 100MW Power Grid against infrastructure health:

| Action | Effect | Cost | Trade-off / Risk |
| :--- | :--- | :--- | :--- |
| `prioritize_hospital` | Max drain Hospital (B) | 30MW, +12°C | Protects life-safety; risks residential flood. |
| `prioritize_residential` | Max drain Residential (A) | 30MW, +12°C | Protects property; risks hospital collapse. |
| `high_pressure_flush` | Resets blockage to 0% | 70MW, +35°C | Restores efficiency; massive thermal spike & **+45% Turbidity penalty**. |
| `harvest_water` | Drains both zones slightly | Zero | **CRITICAL:** Restores +15% Grid Health, BUT destroys filters (-25% Grid) if Turbidity >= 40%. |
| `emergency_cool` | Core temp −25°C | −10% Grid | Prevents meltdown; permanent grid damage. |
| `idle_recharge` | Battery +35MW | Zero | Essential recovery; high flood risk during idle. |

---

## 🎯 Reward Matrix & Triage
The system enforces an ethical hierarchy through mathematically differentiated, clamped rewards:

| Outcome | Reward | Condition |
| :--- | :--- | :--- |
| **Mission Success** | `0.85` | Storm survived, all infrastructure secured. |
| **Strategic Stability** | `~0.55` | Continuous mid-run reward for low risk and harvested water bonuses. |
| **Residential Failure** | `0.35` | Hospital saved, property damage occurred (Ethical Triage). |
| **Critical Failure** | `0.15` | Hospital flooded, hardware meltdown, or Grid collapse. |

---

## 🖥️ Cybernetic Command Center
The environment ships with a real-time SCADA-style dashboard accessible via the root endpoint:
* **CRT Scanline Aesthetic** — mission-control visual style with Orbitron typography.
* **Live Telemetry** — animated trackers for Battery, Core Temp, Blockage, Turbidity, Grid Health, and Zone Water Levels.
* **Urgency Alarms** — blinking pulse alerts and dynamic CSS color-shifting (green/amber/red) on critical thresholds.
* **Sensor Fault Display** — rain bar dims and shows `[SENSOR_FAULT]` in red when telemetry is lost.
* **Smooth Polling** — AJAX fetch every 1.5s; no page reloads.

---

## 💻 How to Run

### Prerequisites
```bash
pip install fastapi uvicorn openai requests
Environment VariablesVariableRequiredDescriptionHF_TOKEN✅API key for the LLM providerMODEL_NAMEOptionalModel to use (default: gpt-4)API_BASE_URLOptionalLLM endpoint (default: https://api.openai.com/v1)1. Start the Environment ServerBashuvicorn server.app:app --host 0.0.0.0 --port 8000
# Dashboard available at http://localhost:8000
2. Run InferenceBashexport HF_TOKEN=your_api_key_here
python inference.py
📁 Project Structurehydraulic_os/
├── inference.py        # Memory-enabled strategic agent
├── server/
│   └── app.py          # Multi-zone physics engine + UI
├── pyproject.toml      # Dependency management
└── README.md