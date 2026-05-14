class Attack:

    def select_seeds(self, agents, graph, config):
        raise NotImplementedError

    def compute_click_probability(self, agent, attack_config):
        raise NotImplementedError