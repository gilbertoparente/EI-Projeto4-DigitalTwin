from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Agent:
    # Atributos Identificadores
    id: int
    name: str
    department: str
    role: str
    hierarchy_level: int

    # Atributos de Comportamento Humano
    education_level: str
    risk_propensity: float  # 0.0 a 1.0
    awareness_level: float  # 0.0 a 1.0 (Nível de consciência/formação)

    # Estado Dinâmico (field permite inicializar listas/dicionários vazios)
    compromised: bool = False
    inbox: List[str] = field(default_factory=list)
    trust_map: Dict[int, float] = field(default_factory=dict)  # ID_Agente -> Nível de Confiança

    # Métricas de simulação (Opcional, mas útil para o teu KPI Service)
    interactions_count: int = 0