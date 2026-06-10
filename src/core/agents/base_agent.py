import mesa


class BaseAgent(mesa.Agent):

    def __init__(
        self,
        unique_id: int,
        model,
        name: str,
        department: str,
        role: str,
        hierarchy_level: int,
        education_level: str,
        risk_propensity: float,
        awareness_level: float,
    ):
        super().__init__(unique_id, model)

        # Identificadores
        self.name = name
        self.department = department
        self.role = role
        self.hierarchy_level = hierarchy_level
        self.education_level = education_level

        # Comportamento humano
        self.risk_propensity = risk_propensity      # 0.0 a 1.0
        self.awareness_level = awareness_level      # 0.0 a 1.0

        self.compromised = False
        self.inbox = []
        self.trust_map: dict[int, float] = {}
        self.interactions_count = 0
