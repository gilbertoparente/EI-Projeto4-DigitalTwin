class Scenario:
    def __init__(
        self,
        num_agents: int,
        num_departments: int,
        hierarchy_structure: str,
        education_distribution: dict,
        trust_distribution: float,
        duration_ticks: int,
        speed: float
    ):
        self.num_agents = num_agents
        self.num_departments = num_departments
        self.hierarchy_structure = hierarchy_structure
        self.education_distribution = education_distribution
        self.trust_distribution = trust_distribution
        self.duration_ticks = duration_ticks
        self.speed = speed