import random
from src.core.domain import Agent


class CollaboratorAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Valores científicos por defeito
        self.defaults = {
            "global_intensity": 0.5,
            "global_training": 0.3,
            "spear_bonus": 0.2,
            "homophily_multiplier": 2.0,
            "role_base": {1: 0.5, 2: 0.6, 3: 0.7},
            "education_profile": {
                "High School": 0.8,
                "Bachelor's Degree": 1.0,
                "Master's / PhD": 1.2,
            },
        }

    def receive_message(self, message, sender):
        params = self.attack_params if self.attack_params else self.defaults

        # 1. Consciência Situacional Individual
        # Consciência = Cargo_base × Perfil_Escolar
        role_base = params.get("role_base", self.defaults["role_base"])
        education_profile = params.get("education_profile", self.defaults["education_profile"])
        cargo_base = role_base.get(self.hierarchy_level, role_base.get(str(self.hierarchy_level), 0.5))
        edu_mod = education_profile.get(self.education_level, 1.0)
        awareness = min(1.0, cargo_base * edu_mod)
        self.awareness_level = awareness

        # 2. Determinar P(Clique) baseada no tipo de ataque
        intensity = params.get("global_intensity", 0.5)
        training = params.get("global_training", 0.3)
        msg_type = getattr(message, 'type', 'Generic')

        if msg_type == "Spear Phishing":
            # P(Clique) = min(1.0, global_intensity + 0.2)
            p_click = min(1.0, intensity + params.get("spear_bonus", 0.2))
        else:
            # P(Clique) = global_intensity × (1 - global_training)
            p_click = intensity * (1 - training)

        # 3. Viés de Homofilia Social
        # Se origem do e-mail == Nó Amigo ⟹ P(Clique) = P(Clique) × 2.0
        trust = self.trust_map.get(sender.id, 0.5)
        if trust > 0.7:
            p_click = p_click * params.get("homophily_multiplier", 2.0)

        final_prob = min(1.0, p_click)

        # Decisão Final
        decision = {"opened": False, "clicked": False, "submitted_credentials": False}
        if random.random() < final_prob:
            decision["opened"] = True
            if random.random() < final_prob:
                decision["clicked"] = True
                if random.random() < (final_prob / 2):
                    decision["submitted_credentials"] = True
                    self.compromised = True
        return decision
