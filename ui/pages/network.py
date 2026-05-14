import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from ui.api_client import get_graph


def show():
    st.title("🕸️ Network Topology View")
    st.markdown("Visualização em tempo real das conexões de confiança e do estado de infeção dos agentes.")

    # 1. Obter dados através do nosso cliente centralizado
    graph_data = get_graph()

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.warning("⚠️ A rede ainda não foi gerada. Por favor, inicie a simulação em 'Experiments'.")
        return

    # 2. Criar o Grafo com NetworkX
    G = nx.Graph()

    for n in nodes:
        # Guardamos o estado e o departamento para usar no desenho/legenda
        G.add_node(n["id"], state=n["state"], dept=n.get("department", "N/A"))

    for e in edges:
        G.add_edge(e["source"], e["target"])

    # 3. Mapeamento de Cores (Estado de Infeção)
    color_map = []
    for _, data in G.nodes(data=True):
        if data["state"] == "infected":
            color_map.append("#FF4B4B")  # Vermelho Streamlit
        else:
            color_map.append("#28A745")  # Verde Sucesso

    # 4. Desenhar o Grafo
    st.subheader("Map de Propagação")

    fig, ax = plt.subplots(figsize=(10, 7))
    # Layout spring: tenta manter nós conectados próximos e evitar sobreposição
    pos = nx.spring_layout(G, seed=42, k=0.3)

    nx.draw(
        G,
        pos,
        node_color=color_map,
        with_labels=False,
        node_size=150,
        edge_color="#DDDDDD",
        width=0.8,
        ax=ax
    )

    # 5. Interface e Estatísticas na Sidebar ou colunas
    st.pyplot(fig)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🟢 Limpo")
    with col2:
        st.error("🔴 Infetado")
    with col3:
        total_inf = sum(1 for n in nodes if n["state"] == "infected")
        st.metric("Total Infetados", f"{total_inf} / {len(nodes)}")

    # 6. Tabela de Detalhes (Opcional, mas útil para o professor ver os dados)
    with st.expander("Ver Detalhes dos Agentes"):
        import pandas as pd
        df_nodes = pd.DataFrame(nodes)
        st.dataframe(df_nodes[["id", "label", "department", "state", "risk"]], use_container_width=True)


if __name__ == "__main__":
    show()