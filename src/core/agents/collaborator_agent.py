import random
from src.core.agents.base_agent import BaseAgent


class CollaboratorAgent(BaseAgent):

    def step(self):
        if not self.inbox:
            return

        message = self.inbox.pop(0)
        sender_id = message.get("sender_id")
        self.interactions_count += 1

        trust     = self.trust_map.get(sender_id, 0.5)
        base_prob = self.risk_propensity * (1 - self.awareness_level)
        final_prob = min(1.0, base_prob + (0.4 * trust))

        if random.random() < final_prob:
            self._become_compromised()

    def _become_compromised(self):
        if not self.model.mfa.apply(self):
            return

        self.compromised = True

        neighbors = self.model.grid.get_neighbors(self.unique_id, include_center=False)
        for neighbor_id in neighbors:
            neighbor = self.model.get_agent(neighbor_id)
            if neighbor is None or not isinstance(neighbor, CollaboratorAgent):
                continue

            if not self.model.segmentation.can_propagate(self, neighbor):
                continue

            weight = self.model.G[self.unique_id][neighbor_id].get("weight", 0.5)
            if random.random() < weight:
                neighbor.inbox.append({"sender_id": self.unique_id})

    def receive_message(self, message: dict):
        self.inbox.append(message)