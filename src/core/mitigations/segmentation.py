import random
from src.core.domain import Agent

class Segmentation:
    def __init__(self, isolation_level: float = 0.5):
        """
        isolation_level: 
        0.0 = rede totalmente aberta (flat network)
        1.0 = totalmente isolada (zero trust)
        """
        self.isolation_level = isolation_level

    def can_propagate(self, agent_from: Agent, agent_to: Agent) -> bool:
        """
        Define se um ataque pode propagar-se entre dois agentes através da rede.
        """
        # Probabilidade base de bloquear o ataque
        block_prob = self.isolation_level

        # Se os agentes forem de departamentos diferentes, a segmentação é 
        # normalmente mais rigorosa (ex: as Finanças não falam com o Marketing)
        if agent_from.department != agent_to.department:
            block_prob += 0.3  # Dificulta a propagação entre departamentos

        # Garante que a probabilidade não excede 100%
        block_prob = min(1.0, block_prob)

        # Se o número aleatório for maior que a probabilidade de bloqueio, o ataque passa
        return random.random() > block_prob

    def limit_breach(self, source_agent: Agent, targets: list[Agent]) -> list[Agent]:
        """
        Filtra uma lista de possíveis alvos, mantendo apenas aqueles 
        onde a segmentação permitiu a passagem do ataque.
        """
        return [target for target in targets if self.can_propagate(source_agent, target)]