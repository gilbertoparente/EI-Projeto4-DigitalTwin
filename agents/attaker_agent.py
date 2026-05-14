import random
from agents.base_agent import Agent


class AttackerAgent(Agent):
    def __init__(self, id, name="Attacker", sophistication=0.7):
        super().__init__(
            id=id,
            name=name,
            department="external",
            role="attacker",
            hierarchy_level=-1,
            education_level="unknown",
            risk_propensity=1.0,
            awareness_level=0.0
        )

        self.sophistication = sophistication
        self.compromised_targets = []

    def select_targets(self, agents, attack_type="phishing"):
        """
        Seleciona alvos dependendo do tipo de ataque.
        """
        if attack_type == "phishing":
            return random.sample(agents, k=min(len(agents), 10))

        if attack_type == "spear_phishing":
            # escolhe alvos mais "valiosos" (hierarquia alta)
            return sorted(
                agents,
                key=lambda a: a.hierarchy_level,
                reverse=True
            )[:3]

        return []

    def launch_attack(self, attack, targets, network_state):
        """
        Executa ataque sobre os alvos.
        """
        results = []

        for agent in targets:
            success_prob = attack.intensity * (1 - agent.awareness_level)

            # amizade aumenta risco (social engineering)
            avg_trust = sum(agent.trust_map.values()) / max(len(agent.trust_map), 1)
            success_prob += 0.2 * avg_trust

            if random.random() < success_prob:
                agent.compromised = True
                self.compromised_targets.append(agent.id)
                results.append((agent.id, True))
            else:
                results.append((agent.id, False))

        return results