from attacks.phishing import PhishingAttack


class SpearPhishingAttack(PhishingAttack):

    def select_seeds(self, agents, graph, config):

        ranked = sorted(
            agents.values(),
            key=lambda x: x["hierarchy"],
            reverse=True
        )

        return [a["id"] for a in ranked[:5]]

    def compute_click_probability(self, agent, attack_config):

        hierarchy_bonus = 1 + (agent["hierarchy"] * 0.15)

        return (
            attack_config["click_rate"]
            * agent["risk"]
            * hierarchy_bonus
        )