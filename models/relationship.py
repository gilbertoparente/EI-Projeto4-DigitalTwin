from dataclasses import dataclass


@dataclass
class Relationship:
    """
    Representa uma relação entre dois agentes no Digital Twin.

    Tipos possíveis:
    - hierarchy  (chefe → subordinado)
    - functional (colaboração de trabalho)
    - social     (amizade/confiança)
    """

    agent_a: int
    agent_b: int
    relation_type: str  # "hierarchy", "functional", "social"

    # intensidade da relação (0 = nenhuma confiança, 1 = máxima confiança)
    weight: float

    # opcional: direção da relação (útil para hierarquia)
    directed: bool = False

    def influence_factor(self) -> float:
        """
        Normaliza o impacto da relação na simulação.
        """

        base = self.weight

        # hierarquia tende a ter mais impacto em spear phishing
        if self.relation_type == "hierarchy":
            base *= 1.2

        # relações sociais amplificam engenharia social
        if self.relation_type == "social":
            base *= 1.3

        # limitar ao intervalo [0, 1]
        return min(1.0, base)