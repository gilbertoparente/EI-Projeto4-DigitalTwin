from mesa import Model
from mesa.datacollection import DataCollector


class DigitalTwinModel(Model):
    def __init__(self, n=150, formacao=0.0, mfa=False):
        super().__init__()
        self.num_agents = n
        self.prob_formacao = formacao
        self.mfa_ativo = mfa
        self.schedule = RandomActivation(self)

        # Coletor de dados para os gráficos
        self.datacollector = DataCollector(
            model_reporters={"Comprometidos": lambda m: self.get_compromised_count()}
        )

    def get_compromised_count(self):
        # Lógica temporária: retorna 0 enquanto não temos agentes
        return 0

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()