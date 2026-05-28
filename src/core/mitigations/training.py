class Training:
    def __init__(self, effectiveness: float = 0.5):

        # 0.0 = formação inútil ou inexistente
        # 1.0 = formação de topo

        self.effectiveness = effectiveness

    def apply(self, agent):

        # Boost inicial aplicado uma vez na criação do agente.
        # Simula formação de integração antes da simulação começar.

        agent.awareness_level = min(
            1.0,
            agent.awareness_level + (self.effectiveness * 0.2),
        )
        agent.risk_propensity = max(
            0.0,
            agent.risk_propensity - (self.effectiveness * 0.1),
        )

    def tick(self, agent):

        # Ajuste gradual chamado a cada tick pelo OrganizationModel.

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
