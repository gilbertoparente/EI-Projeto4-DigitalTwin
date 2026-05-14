from src.core.attacks.phishing import PhishingAttack

class SpearPhishingAttack(PhishingAttack):

    def select_seeds(self, agents, graph, config):
        """
        Seleciona os alvos mais valiosos (VIPs) baseados na hierarquia.
        """
        if not agents:
            return []

        # Ordena os objetos Agent pelo nível de hierarquia (do maior para o menor)
        ranked = sorted(
            agents.values(),
            key=lambda a: a.hierarchy_level,
            reverse=True
        )

        # Retorna apenas os IDs dos top 5 alvos mais importantes
        return [a.id for a in ranked[:5]]

    def compute_click_probability(self, agent, attack_config):
        """
        Calcula a probabilidade com um bónus baseado no cargo (hierarquia).
        Representa ataques mais personalizados para cargos de chefia.
        """
        # Bónus de hierarquia: quanto mais alto o cargo, mais pressão/personalização
        # Usamos o atributo 'hierarchy_level' definido no domain.py
        hierarchy_bonus = 1 + (agent.hierarchy_level * 0.15)

        # Cálculo final usando os atributos do objeto Agent
        return (
            attack_config["click_rate"]
            * agent.risk_propensity
            * hierarchy_bonus
        )