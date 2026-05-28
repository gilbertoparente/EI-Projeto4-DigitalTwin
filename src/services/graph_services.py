from typing import Dict, List


class GraphService:
    """
    Converte o estado interno da simulação num formato
    compatível com D3.js / NetworkX para visualização.

    """

    def get_graph_data(self, agents: Dict, graph_connections: Dict) -> Dict[str, List]:
        nodes = []
        edges = []

        for agent_id, agent in agents.items():
            nodes.append({
                "id":         agent_id,
                "label":      agent.name,
                "department": agent.department,
                "state":      "infected" if agent.compromised else "clean",
                "hierarchy":  agent.hierarchy_level,
                "awareness":  round(agent.awareness_level, 2),
                "risk":       round(agent.risk_propensity, 2),
            })

        seen_edges = set()
        for source_id, connections in graph_connections.items():
            for conn in connections:
                target_id = conn["target"]
                edge_key = tuple(sorted((source_id, target_id)))
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "weight": round(conn.get("weight", 0.5), 2),
                })

        return {"nodes": nodes, "edges": edges}
