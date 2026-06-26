from typing import Dict, List
from src.core.domain import Agent

class Attack:
    def select_seeds(self, agents: Dict[int, Agent], graph: Dict, config: Dict) -> List[int]:
        raise NotImplementedError("select_seeds must be implemented by subclass.")

    def compute_click_probability(self, agent: Agent, attack_config: Dict) -> float:
        raise NotImplementedError("compute_click_probability must be implemented by subclass.")