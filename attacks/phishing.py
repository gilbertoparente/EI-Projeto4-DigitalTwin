import random
from attacks.base_attack import Attack


class PhishingAttack(Attack):

    def select_seeds(self, agents, graph, config):

        n = max(1, len(agents) // 20)

        return random.sample(list(agents.keys()), n)

    def compute_click_probability(self, agent, attack_config):

        return attack_config["click_rate"] * agent["risk"]