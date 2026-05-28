import random
from src.core.agents.base_agent import BaseAgent
from src.core.agents.collaborator_agent import CollaboratorAgent


class AttackerAgent(BaseAgent):

    def __init__(self, unique_id: int, model, sophistication: float = 0.7, attack_type: str = "phishing"):
        super().__init__(
            unique_id=unique_id,
            model=model,
            name="Attacker",
            department="external",
            role="attacker",
            hierarchy_level=-1,
            education_level="N/A",
            risk_propensity=1.0,
            awareness_level=0.0,
        )
        self.sophistication = sophistication
        self.attack_type = attack_type

    def step(self):
        targets = self._select_targets()
        for agent in targets:
            agent.receive_message({"sender_id": self.unique_id})

    def _select_targets(self) -> list:
        collaborators = [
            a for a in self.model.schedule.agents
            if isinstance(a, CollaboratorAgent) and not a.compromised
        ]

        if not collaborators:
            return []

        if self.attack_type == "spear_phishing":
            return sorted(collaborators, key=lambda a: a.hierarchy_level, reverse=True)[:5]

        n = max(1, len(collaborators) // 20)
        return random.sample(collaborators, k=min(len(collaborators), n))
