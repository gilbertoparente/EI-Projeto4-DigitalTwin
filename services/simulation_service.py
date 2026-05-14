import random
from collections import defaultdict

from services.kpi_services import KPIService

from attacks.phishing import PhishingAttack
from attacks.spear_phishing import SpearPhishingAttack


class SimulationService:

    def __init__(self, config):

        self.config = config

        self.tick = 0

        self.kpi_service = KPIService()

        self.agents = {}

        self.graph = defaultdict(list)

        self.metrics = {
            "opened": [],
            "clicked": [],
            "infected": []
        }

        self._build_agents()
        self._build_graph()

    # =====================================================
    # BUILD AGENTS
    # =====================================================

    def _build_agents(self):

        departments = self.config["organization"]["departments"]

        counter = 0

        for dept_index, dept in enumerate(departments):

            for a in dept["agents"]:

                counter += 1

                self.agents[counter] = {
                    "id": counter,
                    "name": a["name"],
                    "department": dept["name"],

                    "risk": a.get("risk", 0.5),
                    "awareness": a.get("awareness", 0.5),

                    "hierarchy": a.get("hierarchy_level", 1),

                    "compromised": False
                }

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    def _build_graph(self):

        ids = list(self.agents.keys())

        for i in ids:
            for j in ids:

                if i == j:
                    continue

                if random.random() < 0.1:

                    self.graph[i].append({
                        "target": j,
                        "weight": random.uniform(0.3, 1.0)
                    })

    # =====================================================
    # ATTACK FACTORY
    # =====================================================

    def _get_attack_model(self):

        attack_type = self.config["attack"]["type"]

        if attack_type == "Spear Phishing":
            return SpearPhishingAttack()

        return PhishingAttack()

    # =====================================================
    # STEP
    # =====================================================

    def step(self):

        self.tick += 1

        attack_config = self.config["attack"]

        defense = self.config["defense"]

        attack_model = self._get_attack_model()

        opened = 0
        clicked = 0
        infected = 0

        seeds = attack_model.select_seeds(
            self.agents,
            self.graph,
            self.config
        )

        visited = set()

        queue = list(seeds)

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            agent = self.agents[current]

            open_prob = (
                attack_config["open_rate"]
                * (1 - agent["awareness"])
            )

            if random.random() < open_prob:

                opened += 1

                click_prob = attack_model.compute_click_probability(
                    agent,
                    attack_config
                )

                if random.random() < click_prob:

                    clicked += 1

                    mfa_block = 0.7 if defense["mfa"] else 0.0

                    compromise_prob = (
                        attack_config["submit_rate"]
                        * (1 - mfa_block)
                    )

                    if random.random() < compromise_prob:

                        infected += 1

                        agent["compromised"] = True

                        for edge in self.graph[current]:

                            if random.random() < edge["weight"]:
                                queue.append(edge["target"])

        self.metrics["opened"].append(opened)
        self.metrics["clicked"].append(clicked)
        self.metrics["infected"].append(infected)

        result = {
            "tick": self.tick,
            "opened": opened,
            "clicked": clicked,
            "infected": infected
        }

        kpis = self.kpi_service.compute(
            result,
            len(self.agents)
        )

        return {
            "result": result,
            "kpis": kpis
        }