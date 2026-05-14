class Training:
    def __init__(self, effectiveness: float = 0.5):
        """
        effectiveness:
        0 = sem formação
        1 = utilizadores altamente treinados
        """
        self.effectiveness = effectiveness

    def apply(self, agent):
        """
        Reduz probabilidade de erro humano.
        """

        # reduz risco de futuro comprometimento
        agent.awareness_level = min(
            1.0,
            agent.awareness_level + self.effectiveness * 0.2
        )

        # reduz propensão ao risco
        agent.risk_propensity = max(
            0.0,
            agent.risk_propensity - self.effectiveness * 0.1
        )

    def reduce_attack_success(self, base_probability: float) -> float:
        """
        Ajusta probabilidade de sucesso de ataques.
        """

        return base_probability * (1 - self.effectiveness)