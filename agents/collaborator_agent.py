import random
from agents.base_agent import BaseAgent


class CollaboratorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def receive_message(self, message, sender):
        """
        Processa emails / mensagens de ataque.
        """

        self.inbox.append(message)

        trust = self.trust_map.get(sender.id, 0.5)

        # probabilidade de interação
        base_prob = self.risk_propensity * (1 - self.awareness_level)

        # confiança social influencia fortemente
        final_prob = base_prob + 0.4 * trust

        decision = {
            "opened": False,
            "clicked": False,
            "submitted_credentials": False
        }

        if random.random() < final_prob:
            decision["opened"] = True

            if random.random() < final_prob:
                decision["clicked"] = True

                if random.random() < final_prob / 2:
                    decision["submitted_credentials"] = True
                    self.compromised = True

        return decision

    def step(self):
        """
        comportamento normal do agente
        """
        pass