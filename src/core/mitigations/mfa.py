import random


class MFA:
    def __init__(self, enabled: bool = True, block_rate: float = 0.9):
        self.enabled    = enabled
        self.block_rate = block_rate

    def apply(self, agent) -> bool:
        if not self.enabled:
            return True

        if random.random() < self.block_rate:
            return False
        return True

    def recover(self, agent):
        if self.enabled and agent.compromised:
            if random.random() < (self.block_rate / 2):
                agent.compromised = False