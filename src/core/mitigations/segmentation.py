import random


class Segmentation:

    def __init__(self, isolation_level: float = 0.5):
        self.isolation_level = isolation_level

    def can_propagate(self, agent_from, agent_to) -> bool:

        # Define se um ataque pode propagar-se de agent_from para agent_to.
        # Departamentos diferentes têm barreira adicional de 30%.

        block_prob = self.isolation_level

        if agent_from.department != agent_to.department:
            block_prob += 0.3  # segmentação inter-departamental

        block_prob = min(1.0, block_prob)
        return random.random() > block_prob

    def limit_breach(self, source_agent, targets: list) -> list:
        # Filtra lista de alvos pelo critério de segmentação.
        return [t for t in targets if self.can_propagate(source_agent, t)]
