from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Agent:
    id: int
    name: str
    department: str
    role: str
    hierarchy_level: int

    education_level: str
    risk_propensity: float
    awareness_level: float

    compromised: bool = False
    inbox: List[str] = field(default_factory=list)

    trust_map: Dict[int, float] = field(default_factory=dict)

    interactions_count: int = 0
    last_compromised_tick: int = -1