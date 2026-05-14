class Agent:
    def __init__(
        self,
        id: int,
        name: str,
        department: str,
        role: str,
        hierarchy_level: int,
        education_level: str,
        risk_propensity: float,
        awareness_level: float
    ):
        self.id = id
        self.name = name
        self.department = department
        self.role = role
        self.hierarchy_level = hierarchy_level

        # comportamento humano
        self.education_level = education_level
        self.risk_propensity = risk_propensity
        self.awareness_level = awareness_level

        # estado dinâmico
        self.compromised = False
        self.inbox = []
        self.trust_map = {}  # relação social com outros agentes