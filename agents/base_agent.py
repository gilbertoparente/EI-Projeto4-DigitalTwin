from mesa import Agent

class BaseCyberAgent(Agent):
    def __init__(self, unique_id, model):
        # Nas versões novas do Mesa, o super().__init__
        # aceita o unique_id e o model desta forma:
        super().__init__(model)
        self.unique_id = unique_id
        self.compromised = False