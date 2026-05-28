import random
import mesa
import mesa.time
import mesa.space
import networkx as nx

from src.core.agents.collaborator_agent import CollaboratorAgent
from src.core.agents.attacker_agent import AttackerAgent
from src.core.mitigations.mfa import MFA
from src.core.mitigations.segmentation import Segmentation
from src.core.mitigations.training import Training


class OrganizationModel(mesa.Model):

    def __init__(self, config: dict, seed: int = None):
        super().__init__(seed=seed)
        self.config = config
        self.tick = 0

        # Defesas
        self.mfa = MFA(enabled=config["defense"].get("mfa", False))
        self.segmentation = Segmentation(isolation_level=config["defense"].get("segmentation", 0.5))
        self.training = Training(effectiveness=config["defense"].get("training", 0.5))
        self._mttd: int | None = None

        # Scheduler: CollaboratorAgents
        # O AttackerAgent é activado explicitamente em step() para garantir
        # que lança os ataques antes dos colaboradores processarem a inbox.
        self.schedule = mesa.time.RandomActivation(self)

        # Grafo social (NetworkX)
        self.G = nx.Graph()

        self._agents_by_id: dict[int, CollaboratorAgent] = {}

        # Construir agentes e grafo
        self._create_collaborators()
        self._build_edges()

        # NetworkGrid integra o grafo NetworkX com o Mesa
        self.grid = mesa.space.NetworkGrid(self.G)
        for agent_id, agent in self._agents_by_id.items():
            self.grid.place_agent(agent, agent_id)

        # Attacker
        attack_type = (
            "spear_phishing"
            if config["attack"]["type"] == "Spear Phishing"
            else "phishing"
        )
        self.attacker = AttackerAgent(
            unique_id=0,
            model=self,
            sophistication=0.7,
            attack_type=attack_type,
        )
        self.G.add_node(0)

        # Regista métricas a cada tick automaticamente
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Compromised": lambda m: sum(
                    1 for a in m.schedule.agents if a.compromised
                ),
                "Interacted": lambda m: sum(
                    1 for a in m.schedule.agents if a.interactions_count > 0
                ),
            },
            agent_reporters={
                "Compromised":   "compromised",
                "Awareness":     "awareness_level",
                "Risk":          "risk_propensity",
                "Interactions":  "interactions_count",
            },
        )

    def _create_collaborators(self):
        counter = 1
        for dept in self.config["organization"]["departments"]:
            for a_data in dept["agents"]:
                agent = CollaboratorAgent(
                    unique_id=counter,
                    model=self,
                    name=a_data["name"],
                    department=dept["name"],
                    role="collaborator",
                    hierarchy_level=a_data.get("hierarchy_level", 1),
                    education_level=a_data.get("education", "BSc"),
                    risk_propensity=a_data.get("risk_propensity", 0.5),
                    awareness_level=a_data.get("awareness_level", 0.5),
                )
                # Formação inicial
                self.training.apply(agent)

                self.G.add_node(counter)
                self.schedule.add(agent)
                self._agents_by_id[counter] = agent
                counter += 1

    def _build_edges(self):
        # Cria o grafo de confiança entre colaboradores.
        ids = list(self._agents_by_id.keys())
        for i in ids:
            for j in ids:
                if i >= j:
                    continue
                prob = (
                    0.3
                    if self._agents_by_id[i].department == self._agents_by_id[j].department
                    else 0.05
                )
                if random.random() < prob:
                    weight = random.uniform(0.4, 0.9)
                    self.G.add_edge(i, j, weight=weight)
                    self._agents_by_id[i].trust_map[j] = weight
                    self._agents_by_id[j].trust_map[i] = weight

    # Loop

    def step(self):

        # Por tick:
        # Recolhe métricas do estado actual
        # Atacante lança campanha
        # Colaboradores processam inbox
        # Formação contínua (pequeno ajuste por tick)

        self.datacollector.collect(self)

        compromised = sum(1 for a in self.schedule.agents if a.compromised)
        if compromised > 0 and self._mttd is None:
            self._mttd = self.tick

        # Ataque
        self.attacker.step()

        # Resposta dos colaboradores
        self.schedule.step()

        # Formação contínua (efeito gradual por tick)
        for agent in self.schedule.agents:
            self.training.tick(agent)

        self.tick += 1
        return self._build_result()

    def _build_result(self) -> dict:
        total = len(self.schedule.agents)
        compromised = sum(1 for a in self.schedule.agents if a.compromised)
        interacted = sum(1 for a in self.schedule.agents if a.interactions_count > 0)

        return {
            "tick": self.tick,
            "result": {
                "opened":   interacted,
                "clicked":  interacted,
                "infected": compromised,
                "mttd":     self._mttd,
            },
            "total_compromised": compromised,
            "total_agents": total,
        }

    def get_agent(self, unique_id: int):
        # Acesso a um agente por ID
        return self._agents_by_id.get(unique_id)

    # Propriedades de compatibilidade com graph_services e rotas existentes
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
        """Compatibilidade com código legado que lê sim.metrics."""
        df = self.datacollector.get_model_vars_dataframe()
        if df.empty:
            return {"opened": [], "clicked": [], "infected": []}
        return {
            "opened":   df["Interacted"].tolist(),
            "clicked":  df["Interacted"].tolist(),
            "infected": df["Compromised"].tolist(),
        }

    @property
    def department_stats(self) -> dict:
        stats = {}
        for agent in self.schedule.agents:
            dept = agent.department
            if dept not in stats:
                stats[dept] = {"total": 0, "compromised": 0}
            stats[dept]["total"] += 1
            if agent.compromised:
                stats[dept]["compromised"] += 1
        for dept in stats:
            t = stats[dept]["total"]
            c = stats[dept]["compromised"]
            stats[dept]["rate"] = round(c / t, 3) if t > 0 else 0.0
        return stats