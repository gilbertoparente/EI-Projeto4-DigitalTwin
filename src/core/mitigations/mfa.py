import random


class MFA:
    def __init__(self, enabled: bool = True, block_rate: float = 0.9):

        # block_rate: Eficácia do MFA em bloquear um acesso não autorizado

        self.enabled = enabled
        self.block_rate = block_rate

    def apply(self, agent) -> bool:

        # Retorna True se o acesso for bem-sucedido.
        # Retorna False se o MFA bloquear a tentativa de invasão.

        if not self.enabled:
            return True

        if random.random() < self.block_rate:
            return False  # MFA bloqueou
        return True  # MFA falhou

    def recover(self, agent):
        if self.enabled and agent.compromised:
            if random.random() < (self.block_rate / 2): # Probabilidade menor de recuperação
                agent.compromised = False