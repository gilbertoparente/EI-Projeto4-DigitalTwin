from typing import Dict, List
from mesa import Agent as BaseAgent


class Attack:

    def select_seeds(self, agents: Dict[int, BaseAgent], graph: Dict, config: Dict) -> List[int]:
        raise NotImplementedError

    def compute_click_probability(self, agent: BaseAgent, attack_config: Dict) -> float:
        raise NotImplementedError