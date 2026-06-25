from typing import Dict, List, Any
from src.core.domain import Agent


class GraphService:
    """
    Transforma o estado interno da simulação num formato
    compatível com bibliotecas de visualização (D3.js, NetworkX, etc).
    """

    def get_graph_data(self, agents: Dict[int, Agent], graph_connections: Dict[int, List[Dict]]) -> Dict[str, List]:
        """
        Gera uma estrutura de 'nodes' e 'edges'.
        """
        nodes = []
        edges = []

        # 1. Processar os Nós (Agentes)
        for agent_id, agent in agents.items():
            # Definimos a cor ou estado para o grafo
            state = "infected" if agent.compromised else "clean"

            nodes.append({
                "id": agent_id,
                "label": agent.name,
                "department": agent.department,
                "state": state,
                "hierarchy": agent.hierarchy_level,
                "hierarchy_level": agent.hierarchy_level,
                # Atributos extras para tooltips na UI
                "awareness": round(agent.awareness_level, 2),
                "risk": round(agent.risk_propensity, 2)
            })

        # 2. Processar as Arestas (Conexões de confiança/rede)
        for source_id, connections in graph_connections.items():
            for conn in connections:
                edges.append({
                    "source": source_id,
                    "target": conn["target"],
                    "weight": round(conn.get("weight", 0.5), 2)
                })

        return {
            "nodes": nodes,
            "edges": edges
        }
