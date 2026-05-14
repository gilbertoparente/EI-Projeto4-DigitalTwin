from typing import Dict, List
# Importamos a classe Agent para que o Python saiba o que é o parâmetro 'agent'
from src.core.domain import Agent

class Attack:
    """
    Classe base que define a interface para todos os modelos de ataque.
    """

    def select_seeds(self, agents: Dict[int, Agent], graph: Dict, config: Dict) -> List[int]:
        """
        Deve retornar uma lista de IDs de agentes que serão os alvos iniciais.
        """
        raise NotImplementedError("O método select_seeds deve ser implementado pela subclasse.")

    def compute_click_probability(self, agent: Agent, attack_config: Dict) -> float:
        """
        Deve retornar um valor entre 0.0 e 1.0 representando a probabilidade de sucesso.
        """
        raise NotImplementedError("O método compute_click_probability deve ser implementado pela subclasse.")