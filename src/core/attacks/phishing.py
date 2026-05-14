import random
from src.core.attacks.base_attack import Attack


class PhishingAttack(Attack):

    def select_seeds(self, agents, graph, config):
        """
        Seleciona aleatoriamente 5% dos agentes (seeds) para iniciar a propagação.
        """
        if not agents:
            return []

        # Seleciona IDs (chaves do dicionário de agentes)
        agent_ids = list(agents.keys())
        n = max(1, len(agent_ids) // 20)  # 5% da população

        return random.sample(agent_ids, n)

    def compute_click_probability(self, agent, attack_config):
        """
        Calcula a probabilidade de um agente clicar no link.
        agent: Instância da classe Agent ou CollaboratorAgent
        attack_config: Dicionário vindo da UI (ex: {"click_rate": 0.5})
        """
        # Ajuste importante: 'agent' agora é um objeto, usamos o ponto (.)
        # e o nome do atributo definido no domain.py é 'risk_propensity'
        return attack_config["click_rate"] * agent.risk_propensity