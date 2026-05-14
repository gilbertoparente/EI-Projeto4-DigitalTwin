import random
from typing import Dict, List
from src.core.domain import Agent
from src.core.agents.collaborator_agent import CollaboratorAgent
from src.core.attacks.phishing import PhishingAttack
from src.core.attacks.spear_phishing import SpearPhishingAttack
from src.core.mitigations.mfa import MFA
from src.core.mitigations.segmentation import Segmentation
from src.core.mitigations.training import Training


class SimulationService:
    def __init__(self, config: dict):
        self.config = config
        self.tick = 0
        self.agents: Dict[int, CollaboratorAgent] = {}
        self.graph = {}  # ID -> List of neighbors
        self.metrics = {"opened": [], "clicked": [], "infected": []}

        # Inicializar Defesas
        self.mfa = MFA(enabled=config["defense"].get("mfa", False))
        self.segmentation = Segmentation(isolation_level=config["defense"].get("segmentation", 0.5))
        self.training = Training(effectiveness=config["defense"].get("training", 0.5))

        self._initialize_model()

    def _initialize_model(self):
        """Cria os agentes e a rede social inicial."""
        counter = 0
        for dept in self.config["organization"]["departments"]:
            for a_data in dept["agents"]:
                counter += 1
                # Criamos a instância do CollaboratorAgent (que herda de Agent)
                agent = CollaboratorAgent(
                    id=counter,
                    name=a_data["name"],
                    department=dept["name"],
                    role="collaborator",
                    hierarchy_level=a_data.get("hierarchy_level", 1),
                    education_level=a_data.get("education", "BSc"),
                    risk_propensity=a_data.get("risk_propensity", 0.5),
                    awareness_level=a_data.get("awareness_level", 0.5)
                )

                # Aplicar treino inicial (ajusta awareness/risk antes de começar)
                self.training.apply(agent)

                self.agents[counter] = agent

        # Criar grafo de relações (quem confia em quem)
        for i in self.agents:
            self.graph[i] = []
            for j in self.agents:
                if i != j:
                    # Probabilidade de conexão (maior se for do mesmo departamento)
                    prob = 0.3 if self.agents[i].department == self.agents[j].department else 0.05
                    if random.random() < prob:
                        weight = random.uniform(0.4, 0.9)
                        self.graph[i].append({"target": j, "weight": weight})
                        # Atualizar trust_map interno do agente para a lógica de decisão
                        self.agents[i].trust_map[j] = weight

    def _get_attack_model(self):
        """Seleciona o modelo de ataque com base na configuração."""
        attack_type = self.config["attack"]["type"]
        if attack_type == "Spear Phishing":
            return SpearPhishingAttack()
        return PhishingAttack()

    def step(self):
        """Executa um passo da simulação (um dia ou uma campanha de ataque)."""
        self.tick += 1
        attack_config = self.config["attack"]
        attack_model = self._get_attack_model()

        # 1. Selecionar alvos iniciais (Seeds)
        seeds = attack_model.select_seeds(self.agents, self.graph, self.config)

        opened_this_step = 0
        clicked_this_step = 0
        infected_this_step = 0

        queue = list(seeds)
        visited = set()

        while queue:
            curr_id = queue.pop(0)
            if curr_id in visited:
                continue
            visited.add(curr_id)

            agent = self.agents[curr_id]

            # 2. O agente processa o ataque (Fator Humano)
            # Simulamos o remetente como o próprio modelo de ataque
            decision = agent.receive_message("Phishing Campaign", sender=agent)

            if decision["opened"]:
                opened_this_step += 1

                if decision["clicked"]:
                    clicked_this_step += 1

                    # 3. Defesa Técnica: MFA
                    # Se o MFA estiver ativo e bloquear, o ataque morre aqui
                    if self.mfa.apply(agent):

                        if decision["submitted_credentials"]:
                            if not agent.compromised:  # Evitar contar duas vezes
                                agent.compromised = True
                                infected_this_step += 1

                            # 4. Propagação Lateral (Movimento Lateral)
                            for edge in self.graph[curr_id]:
                                target_id = edge["target"]
                                target_agent = self.agents[target_id]

                                # A Segmentação de Rede pode bloquear a propagação
                                if self.segmentation.can_propagate(agent, target_agent):
                                    if random.random() < edge["weight"]:
                                        queue.append(target_id)

        # Guardar métricas para gráficos
        self.metrics["opened"].append(opened_this_step)
        self.metrics["clicked"].append(clicked_this_step)
        self.metrics["infected"].append(infected_this_step)

        return {
            "tick": self.tick,
            "result": {
                "opened": opened_this_step,
                "clicked": clicked_this_step,
                "infected": infected_this_step
            },
            "total_compromised": sum(1 for a in self.agents.values() if a.compromised)
        }