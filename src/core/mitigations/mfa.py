import random
from src.core.domain import Agent

class MFA:
    def __init__(self, enabled: bool = True, block_rate: float = 0.9):
        """
        enabled: Se o MFA está ativo na organização.
        block_rate: Eficácia do MFA em bloquear um acesso não autorizado (ex: 90%).
        """
        self.enabled = enabled
        self.block_rate = block_rate

    def apply(self, agent: Agent) -> bool:
        """
        Retorna True se o acesso for bem-sucedido.
        Retorna False se o MFA bloquear a tentativa de invasão.
        """
        if not self.enabled:
            return True # Sem MFA, o atacante passa sempre se tiver as credenciais

        # O MFA entra em ação quando o atacante tenta usar as credenciais
        # (representado pelo estado compromised do agente)
        if agent.compromised:
            if random.random() < self.block_rate:
                # MFA bloqueou o acesso!
                return False

        return True

    def recover(self, agent: Agent):
        """
        Simula a recuperação de uma conta. Se o MFA detetar atividade suspeita,
        pode forçar o reset do estado do agente.
        """
        if self.enabled and agent.compromised:
            if random.random() < (self.block_rate / 2): # Probabilidade menor de auto-recuperação
                agent.compromised = False