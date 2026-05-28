from dataclasses import dataclass


@dataclass
class Relationship:

    # Tipos possíveis:
    # hierarchy  (chefe → subordinado)
    # functional (colaboração de trabalho)
    # social     (amizade/confiança)

    agent_a: int
    agent_b: int
    relation_type: str  # "hierarchy", "functional", "social"

    # 0 = confiança mínima, 1 = confiança máxima
    weight: float

    # opcional: direção da relação (útil para hierarquia)
    directed: bool = False

    def influence_factor(self) -> float:

        base = self.weight

        if self.relation_type == "hierarchy":
            base *= 1.2

        if self.relation_type == "social":
            base *= 1.3

        return min(1.0, base)