import random
import mesa
import mesa.time
import mesa.space
import networkx as nx

from src.core.agents.collaborator_agent import CollaboratorAgent
from src.core.agents.attaker_agent import AttackerAgent
from src.core.mitigations.mfa import MFA
from src.core.mitigations.segmentation import Segmentation
from src.core.mitigations.training import Training

EDUCATION_AWARENESS_MOD = {
    "High School":       0.8,
    "Bachelor's Degree": 1.0,
    "Master's / PhD":    1.2,
}


class OrganizationModel(mesa.Model):

    def __init__(self, config: dict, seed: int = None):
        super().__init__(seed=seed)
        self.config = config
        self.tick   = 0

        defense = config.get("defense", {})
        self.mfa          = MFA(enabled=defense.get("mfa", False))
        self.segmentation = Segmentation(isolation_level=defense.get("segmentation", 0.5))
        self.training     = Training(effectiveness=defense.get("training", 0.5))
        self._mttd: int | None = None

        self.schedule = mesa.time.RandomActivation(self)

        self.G = nx.Graph()
        self._agents_by_id: dict[int, CollaboratorAgent] = {}

        self._create_collaborators()
        self._build_edges()

        self.grid = mesa.space.NetworkGrid(self.G)
        for agent_id, agent in self._agents_by_id.items():
            self.grid.place_agent(agent, agent_id)

        attack_type = (
            "spear_phishing"
            if config.get("attack", {}).get("type") == "Spear Phishing"
            else "phishing"
        )
        self.attacker = AttackerAgent(
            unique_id=0,
            model=self,
            sophistication=0.7,
            attack_type=attack_type,
        )
        self.G.add_node(0)

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Compromised": lambda m: sum(1 for a in m.schedule.agents if a.compromised),
                "Interacted":  lambda m: sum(1 for a in m.schedule.agents if a.interactions_count > 0),
            },
            agent_reporters={
                "Compromised":  "compromised",
                "Awareness":    "awareness_level",
                "Risk":         "risk_propensity",
                "Interactions": "interactions_count",
                "Education":    "education_level",
                "Department":   "department",
                "Hierarchy":    "hierarchy_level",
            },
        )

    def _create_collaborators(self):
        counter = 1
        for dept in self.config.get("organization", {}).get("departments", []):
            for a_data in dept.get("agents", []):
                education = a_data.get("education_level", a_data.get("education", "Bachelor's Degree"))

                agent = CollaboratorAgent(
                    unique_id=counter,
                    model=self,
                    name=a_data.get("name", f"Agent_{counter}"),
                    department=dept.get("name", "General"),
                    role="collaborator",
                    hierarchy_level=a_data.get("hierarchy_level", 1),
                    education_level=education,
                    risk_propensity=a_data.get("risk_propensity", 0.5),
                    awareness_level=a_data.get("awareness_level", 0.5),
                )

                self.training.apply(agent)

                self.G.add_node(counter)
                self.schedule.add(agent)
                self._agents_by_id[counter] = agent
                counter += 1

    def _build_edges(self):
        ids = list(self._agents_by_id.keys())
        for i in ids:
            for j in ids:
                if i >= j:
                    continue
                same_dept = self._agents_by_id[i].department == self._agents_by_id[j].department
                prob = 0.3 if same_dept else 0.05
                if random.random() < prob:
                    weight = random.uniform(0.4, 0.9)
                    self.G.add_edge(i, j, weight=weight)
                    self._agents_by_id[i].trust_map[j] = weight
                    self._agents_by_id[j].trust_map[i] = weight

    def step(self) -> dict:
        self.attacker.step()

        self.schedule.step()

        for agent in self.schedule.agents:
            self.training.tick(agent)

        self.tick += 1

        compromised = sum(1 for a in self.schedule.agents if a.compromised)
        if compromised > 0 and self._mttd is None:
            self._mttd = self.tick

        self.datacollector.collect(self)

        return self._build_result()

    def _build_result(self) -> dict:
        total       = len(self.schedule.agents)
        compromised = sum(1 for a in self.schedule.agents if a.compromised)
        interacted  = sum(1 for a in self.schedule.agents if a.interactions_count > 0)

        return {
            "tick":              self.tick,
            "result": {
                "opened":   interacted,
                "clicked":  compromised,
                "infected": compromised,
                "mttd":     self._mttd,
            },
            "total_compromised": compromised,
            "total_agents":      total,
        }

    def get_agent(self, unique_id: int):
        return self._agents_by_id.get(unique_id)

    @property
    def agents(self) -> dict:
        return dict(self._agents_by_id)

    @property
    def graph(self) -> dict:
        result = {}
        for node in self.G.nodes:
            if node == 0:
                continue
            result[node] = [
                {"target": nb, "weight": self.G[node][nb].get("weight", 0.5)}
                for nb in self.G.neighbors(node)
                if nb != 0
            ]
        return result

    @property
    def metrics(self) -> dict:
        df = self.datacollector.get_model_vars_dataframe()
        if df.empty:
            return {"opened": [], "clicked": [], "infected": []}
        return {
            "opened":   df["Interacted"].tolist(),
            "clicked":  df["Compromised"].tolist(),
            "infected": df["Compromised"].tolist(),
        }

    @property
    def department_stats(self) -> dict:
        stats = {}
        for agent in self.schedule.agents:
            dept = agent.department
            if dept not in stats:
                stats[dept] = {"total": 0, "compromised": 0, "education_breakdown": {}}
            stats[dept]["total"] += 1
            if agent.compromised:
                stats[dept]["compromised"] += 1
            edu = agent.education_level
            stats[dept]["education_breakdown"][edu] = stats[dept]["education_breakdown"].get(edu, 0) + 1

        for dept in stats:
            t = stats[dept]["total"]
            c = stats[dept]["compromised"]
            stats[dept]["rate"] = round(c / t, 3) if t > 0 else 0.0
        return stats