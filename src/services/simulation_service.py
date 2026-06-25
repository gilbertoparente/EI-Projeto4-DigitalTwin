import random

from src.core.agents.collaborator_agent import CollaboratorAgent
from src.core.mitigations.mfa import MFA
from src.core.mitigations.segmentation import Segmentation
from src.core.mitigations.training import Training


class SimulationService:
    def __init__(self, config: dict):
        self.config = config
        self.tick = 0
        self.agents = {}
        self.graph = {}
        self.metrics = {"opened": [], "clicked": [], "infected": []}
        self.attack_params = self.config.get("attack_params", {})

        defense_config = self.config.get("defense", {})
        self.mfa = MFA(enabled=defense_config.get("mfa", False))
        self.segmentation = Segmentation(isolation_level=defense_config.get("segmentation", 0.5))
        self.training = Training(
            effectiveness=defense_config.get("training", self.attack_params.get("global_training", 0.3))
        )
        self.training_coverage = defense_config.get("training_coverage", 0.0)

        self._initialize_model()

    def _initialize_model(self):
        counter = 0
        for dept in self.config.get("organization", {}).get("departments", []):
            for agent_data in dept.get("agents", []):
                counter += 1
                agent = CollaboratorAgent(
                    id=counter,
                    name=agent_data.get("name", "User"),
                    department=dept.get("name", "General"),
                    role="collaborator",
                    hierarchy_level=agent_data.get("hierarchy_level", 1),
                    education_level=agent_data.get("education_level", agent_data.get("education", "Bachelor's Degree")),
                    risk_propensity=agent_data.get("risk_propensity", 0.5),
                    awareness_level=agent_data.get("awareness_level", 0.5),
                    trust_links_count=agent_data.get("trust_links_count", 3),
                    attack_params=dict(self.attack_params),
                )
                if random.random() < self.training_coverage:
                    self.training.apply(agent)
                    agent.attack_params["global_training"] = self.training.effectiveness
                else:
                    agent.attack_params["global_training"] = 0.0
                self.agents[counter] = agent

        self._build_graph()

    def _build_graph(self):
        for source_id, source in self.agents.items():
            possible_targets = [agent_id for agent_id in self.agents if agent_id != source_id]
            random.shuffle(possible_targets)
            desired_links = min(source.trust_links_count, len(possible_targets))
            self.graph[source_id] = []

            for target_id in possible_targets[:desired_links]:
                target = self.agents[target_id]
                same_dept = source.department == target.department
                weight = random.uniform(0.65, 0.95) if same_dept else random.uniform(0.35, 0.7)
                self.graph[source_id].append({"target": target_id, "weight": weight})
                source.trust_map[target_id] = weight

    def step(self):
        self.tick += 1
        opened_this_step = 0
        clicked_this_step = 0
        infected_this_step = 0
        message = type("Msg", (object,), {"type": self.config.get("attack", {}).get("type", "Generic")})

        target_ids = list(self.agents.keys())
        random.shuffle(target_ids)

        for agent_id in target_ids:
            agent = self.agents[agent_id]
            sender = self._choose_sender(agent_id)
            was_compromised = agent.compromised
            decision = agent.receive_message(message=message, sender=sender)

            if decision["opened"]:
                opened_this_step += 1
            if decision["clicked"]:
                clicked_this_step += 1
            if decision["submitted_credentials"] and not was_compromised:
                if self.mfa.apply(agent):
                    infected_this_step += 1
                else:
                    agent.compromised = False

        self.metrics["opened"].append(opened_this_step)
        self.metrics["clicked"].append(clicked_this_step)
        self.metrics["infected"].append(infected_this_step)

        return {
            "tick": self.tick,
            "result": {
                "opened": opened_this_step,
                "clicked": clicked_this_step,
                "infected": infected_this_step,
            },
            "total_compromised": sum(1 for agent in self.agents.values() if agent.compromised),
        }

    def _choose_sender(self, agent_id):
        agent = self.agents[agent_id]
        trusted_ids = list(agent.trust_map)
        if not trusted_ids:
            return agent

        sender_id = random.choice(trusted_ids)
        sender = self.agents[sender_id]
        if self.segmentation.can_propagate(sender, agent):
            return sender
        return agent
