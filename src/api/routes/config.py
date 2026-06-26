from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    n_agents: int = Field(default=150, ge=10, le=500)
    formation_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    mfa_enabled: bool = Field(default=False)
    attack_type: str = Field(default="mass")  # "mass" or "spear"