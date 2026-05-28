import streamlit as st
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from ui.api_client import get_graph


def show():
    st.markdown("""
    <h1 style='margin-bottom:.25rem'>🕸️ Network</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Visualização em tempo real das conexões de confiança e do estado de infeção dos agentes.
    </p>
    """, unsafe_allow_html=True)

    if st.button("🔄 Atualizar grafo"):
        st.rerun()

    graph_data = get_graph()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.warning("⚠️ A rede ainda não foi gerada. Inicie a simulação em **Experiments**.")
        return

    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"], state=n["state"], dept=n.get("department", "N/A"))
    for e in edges:
        G.add_edge(e["source"], e["target"])

    color_map = [
        "#f85149" if G.nodes[n]["state"] == "infected" else "#3fb950"
        for n in G.nodes
    ]

    col_graph, col_stats = st.columns([3, 1])

    with col_graph:
        fig, ax = plt.subplots(figsize=(9, 6))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")
        pos = nx.spring_layout(G, seed=42, k=0.3)
        nx.draw(
            G, pos,
            node_color=color_map,
            with_labels=False,
            node_size=120,
            edge_color="#30363d",
            width=0.7,
            ax=ax
        )
        st.pyplot(fig)
        plt.close(fig)

    with col_stats:
        total_inf = sum(1 for n in nodes if n["state"] == "infected")
        total_clean = len(nodes) - total_inf

        st.metric("Total de agentes", len(nodes))
        st.metric("🟢 Limpos",   total_clean)
        st.metric("🔴 Infetados", total_inf)

        if len(nodes) > 0:
            pct = round(total_inf / len(nodes) * 100, 1)
            st.progress(total_inf / len(nodes), text=f"Infeção: {pct}%")

        # Departamentos
        dept_counts = {}
        for n in nodes:
            d = n.get("department", "N/A")
            dept_counts[d] = dept_counts.get(d, {"total": 0, "inf": 0})
            dept_counts[d]["total"] += 1
            if n["state"] == "infected":
                dept_counts[d]["inf"] += 1

        st.markdown("<p style='font-size:12px; color:#6e7681; margin:1rem 0 .25rem'>Por departamento</p>",
                    unsafe_allow_html=True)
        for dept, c in dept_counts.items():
            rate = round(c["inf"] / max(c["total"], 1) * 100)
            color = "#f85149" if rate > 50 else "#e3b341" if rate > 20 else "#3fb950"
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"font-size:12px;padding:3px 0;border-bottom:1px solid #21262d'>"
                f"<span style='color:#c9d1d9'>{dept}</span>"
                f"<span style='color:{color};font-weight:600'>{rate}%</span></div>",
                unsafe_allow_html=True
            )

    with st.expander("📋 Detalhes dos agentes"):
        df_nodes = pd.DataFrame(nodes)
        cols = [c for c in ["id", "label", "department", "state", "hierarchy", "awareness", "risk"]
                if c in df_nodes.columns]
        st.dataframe(df_nodes[cols], use_container_width=True)
