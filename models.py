from openenv.core import Action, Observation, State as BaseState
from pydantic import Field
from typing import List, Dict, Any

class UniversalAgentAction(Action):
    model_config = {"extra": "ignore"}
    message: str = Field(default="Smart Mitigation Active")
    gate_id: int = Field(0)
    command: str = Field("neutral")
    pump_power: float = Field(0.0)

class UniversalAgentObservation(Observation):
    model_config = {"extra": "ignore"}
    reward: float = Field(0.0)
    done: bool = Field(False)
    # 💥 THE PIPE: This string will carry our hidden JSON data
    status: str = Field(default="{}")
    info: Dict[str, Any] = Field(default_factory=dict)

class State(BaseState):
    model_config = {"extra": "ignore"}
    episode_id: str = Field("dummy-uuid")
    step_count: int = Field(0)
    sector_levels: List[float] = Field(default_factory=lambda: [0.2, 0.3, 0.2, 0.4, 0.1])
    active_rainfall: float = Field(10.0)
    gates_open: List[bool] = Field(default_factory=lambda: [False]*5)