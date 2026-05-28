import random
from mesa import Agent as BaseAgent


class Segmentation:
    def __init__(self, isolation_level: float = 0.5):
        self.isolation_level = isolation_level

    def can_propagate(self, agent_from: BaseAgent, agent_to: BaseAgent) -> bool:
        block_prob = self.isolation_level

        if agent_from.department != agent_to.department:
            block_prob += 0.3

        block_prob = min(1.0, block_prob)

        return random.random() > block_prob

    def limit_breach(self, source_agent: BaseAgent, targets: list[BaseAgent]) -> list[BaseAgent]:
        return [target for target in targets if self.can_propagate(source_agent, target)]