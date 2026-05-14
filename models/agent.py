from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Agent:
    """
    Representa um agente (colaborador) no Digital Twin.
    Apenas estado + atributos estruturais.
    NÃO contém lógica de simulação.
    """

    id: int
    name: str
    department: str
    role: str
    hierarchy_level: int

    education_level: str
    risk_propensity: float
    awareness_level: float

    # Estado dinâmico (alterado pela simulação)
    compromised: bool = False
    inbox: List[str] = field(default_factory=list)

    # Relações sociais (confiança entre agentes)
    trust_map: Dict[int, float] = field(default_factory=dict)

    # Métricas locais (opcional, útil para análise)
    interactions_count: int = 0
    last_compromised_tick: int = -1