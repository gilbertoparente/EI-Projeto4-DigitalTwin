from src.core.attacks.phishing import PhishingAttack


class SpearPhishingAttack(PhishingAttack):

    def select_seeds(self, agents, graph, config):
        if not agents:
            return []

        ranked = sorted(
            agents.values(),
            key=lambda a: a.hierarchy_level,
            reverse=True
        )

        return [a.unique_id for a in ranked[:5]]

    def compute_click_probability(self, agent, attack_config):
        hierarchy_bonus = 1 + (agent.hierarchy_level * 0.15)

        return (
            attack_config["click_rate"]
            * agent.risk_propensity
            * hierarchy_bonus
        )