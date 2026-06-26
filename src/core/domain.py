from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Agent:
    # Legacy dataclass kept for backward-compatibility imports.
    id: int
    name: str
    department: str
    role: str
    hierarchy_level: int
    education_level: str
    risk_propensity: float
    awareness_level: float
    trust_links_count: int = 3
    attack_params: Dict = field(default_factory=dict)

    compromised: bool = False
    inbox: List[str] = field(default_factory=list)
    trust_map: Dict[int, float] = field(default_factory=dict)