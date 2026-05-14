class Segmentation:
    def __init__(self, isolation_level: float = 0.5):
        """
        isolation_level:
        0 = rede totalmente aberta
        1 = totalmente isolada
        """
        self.isolation_level = isolation_level

    def can_propagate(self, agent_from, agent_to) -> bool:
        """
        Define se um ataque pode propagar entre dois agentes.
        """

        import random

        # quanto maior a segmentação, menor propagação
        block_prob = self.isolation_level

        if agent_from.department != agent_to.department:
            block_prob += 0.3  # travar cross-department

        return random.random() > block_prob

    def limit_breach(self, compromised_agents, all_agents):
        """
        Remove propagação lateral com base na segmentação.
        """

        allowed = []

        for a in compromised_agents:
            for b in all_agents:
                if self.can_propagate(a, b):
                    allowed.append(b)

        return allowed