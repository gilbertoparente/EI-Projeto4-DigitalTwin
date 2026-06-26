class Training:

    def __init__(self, effectiveness: float = 0.5):
        self.effectiveness = effectiveness

    def apply(self, agent):
        agent.awareness_level = min(
            1.0,
            agent.awareness_level + (self.effectiveness * 0.2),
        )
        agent.risk_propensity = max(
            0.0,
            agent.risk_propensity - (self.effectiveness * 0.1),
        )

    def tick(self, agent):
        agent.awareness_level = min(
            1.0,
            agent.awareness_level + (self.effectiveness * 0.01),
        )
        agent.risk_propensity = max(
            0.0,
            agent.risk_propensity - (self.effectiveness * 0.005),
        )

    def reduce_attack_success(self, base_probability: float) -> float:
        return base_probability * (1 - self.effectiveness)