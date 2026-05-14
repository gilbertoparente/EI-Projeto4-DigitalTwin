import random
# Importamos a classe base do local correto
from src.core.domain import Agent


class CollaboratorAgent(Agent):
    def __init__(self, *args, **kwargs):
        # O super().__init__ vai preencher automaticamente os campos da dataclass
        super().__init__(*args, **kwargs)

    def receive_message(self, message, sender):
        """
        Lógica de decisão baseada em risco, consciência e confiança social.
        """
        self.inbox.append(message)

        # Se o remetente não estiver no trust_map, assumimos confiança neutra (0.5)
        trust = self.trust_map.get(sender.id, 0.5)

        # Probabilidade base: propensão ao risco vs. nível de formação
        # Se awareness_level for 1.0 (muita formação), a prob base vai para 0.
        base_prob = self.risk_propensity * (1 - self.awareness_level)

        # A engenharia social (confiança) aumenta a probabilidade de cair no erro
        final_prob = base_prob + (0.4 * trust)

        # Garantir que a probabilidade não ultrapassa 1.0 (100%)
        final_prob = min(1.0, final_prob)

        decision = {
            "opened": False,
            "clicked": False,
            "submitted_credentials": False
        }

        # Simulação da "cadeia de erro" do utilizador
        if random.random() < final_prob:
            decision["opened"] = True

            # Se abriu, pode clicar
            if random.random() < final_prob:
                decision["clicked"] = True

                # Se clicou, pode submeter dados (mais difícil, por isso / 2)
                if random.random() < (final_prob / 2):
                    decision["submitted_credentials"] = True
                    self.compromised = True

        return decision

    def step(self):
        """
        Aqui podes adicionar comportamentos autónomos,
        como interagir com colegas ou aumentar o awareness com o tempo.
        """
        pass