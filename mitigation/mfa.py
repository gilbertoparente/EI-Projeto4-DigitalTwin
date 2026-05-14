class MFA:
    def __init__(self, enabled: bool = True, block_rate: float = 0.9):
        self.enabled = enabled
        self.block_rate = block_rate

    def apply(self, agent) -> bool:
        """
        Retorna True se acesso for permitido.
        Se MFA estiver ativo, reduz impacto de compromissos.
        """

        if not self.enabled:
            return True

        # Se agente está comprometido, MFA pode bloquear exploração
        if agent.compromised:
            import random
            if random.random() < self.block_rate:
                # bloqueia exploração do ataque
                return False

        return True

    def recover(self, agent):
        """
        Pode reverter ou mitigar estado comprometido (simulação simplificada)
        """
        if self.enabled and agent.compromised:
            import random
            if random.random() < self.block_rate:
                agent.compromised = False