import mesa

EDUCATION_AWARENESS_MOD = {
    "High School":       0.8,
    "Bachelor's Degree": 1.0,
    "Master's / PhD":    1.2,
}

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

        self.name            = name
        self.department      = department
        self.role            = role
        self.hierarchy_level = hierarchy_level
        self.education_level = education_level  # "High School" | "Bachelor's Degree" | "Master's / PhD"

        self.risk_propensity = risk_propensity
        edu_mod = EDUCATION_AWARENESS_MOD.get(education_level, 1.0)
        self.awareness_level = min(1.0, awareness_level * edu_mod)

        self.compromised        = False
        self.inbox              = []
        self.trust_map: dict[int, float] = {}
        self.interactions_count = 0