from src.core.domain import Agent

class Training:
    def __init__(self, effectiveness: float = 0.5):
        """
        effectiveness:
        0.0 = Formação inútil ou inexistente.
        1.0 = Formação de elite (utilizadores sabem detetar qualquer phishing).
        """
        self.effectiveness = effectiveness

    def apply(self, agent: Agent):
        """
        Aplica a formação ao agente, alterando as suas propriedades permanentemente.
        """
        # Aumenta o nível de consciência (awareness)
        # O bónus depende da eficácia da formação (máximo +0.2 por sessão)
        agent.awareness_level = min(
            1.0,
            agent.awareness_level + (self.effectiveness * 0.2)
        )

        # Reduz a propensão ao risco
        # Utilizadores treinados tornam-se mais cautelosos
        agent.risk_propensity = max(
            0.0,
            agent.risk_propensity - (self.effectiveness * 0.1)
        )

    def reduce_attack_success(self, base_probability: float) -> float:
        """
        Calcula o impacto direto da formação na probabilidade de sucesso de um ataque.
        """
        # Se effectiveness for 1.0, a probabilidade cai para 0.
        return base_probability * (1 - self.effectiveness)