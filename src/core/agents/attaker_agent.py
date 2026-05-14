import random
# O segredo está aqui: importamos do novo local centralizado
from src.core.domain import Agent

class AttackerAgent(Agent):
    def __init__(self, id: int, name="Attacker", sophistication=0.7):
        # Chamamos o super() com os campos que o nosso dataclass Agent exige
        super().__init__(
            id=id,
            name=name,
            department="external",
            role="attacker",
            hierarchy_level=-1,
            risk_propensity=1.0,
            awareness_level=0.0
        )
        self.sophistication = sophistication
        self.compromised_targets = []

    def select_targets(self, agents_list, attack_type="phishing"):
        """
        Seleciona alvos da lista de objetos Agent.
        """
        if not agents_list:
            return []

        if attack_type == "phishing":
            # Seleciona 10 agentes aleatórios da simulação
            return random.sample(agents_list, k=min(len(agents_list), 10))

        if attack_type == "spear_phishing":
            # Escolhe os 3 com maior nível hierárquico
            return sorted(
                agents_list,
                key=lambda a: a.hierarchy_level,
                reverse=True
            )[:3]

        return []

    def launch_attack(self, attack_intensity, targets):
        """
        Executa o ataque. Nota: 'attack_intensity' substitui o objeto 'attack'
        para simplificar, ou podes passar o objeto de src.core.attacks.
        """
        results = []

        for agent in targets:
            # Lógica: Quanto menor a consciência (awareness), maior a chance
            success_prob = attack_intensity * (1 - agent.awareness_level)

            # Engenharia Social: Confiança média nos outros aumenta o risco
            if agent.trust_map:
                avg_trust = sum(agent.trust_map.values()) / len(agent.trust_map)
                success_prob += 0.2 * avg_trust

            if random.random() < success_prob:
                agent.compromised = True
                self.compromised_targets.append(agent.id)
                results.append((agent.id, True))
            else:
                results.append((agent.id, False))

        return results