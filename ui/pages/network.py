import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from ui.api_client import get_graph


def draw_topology_graph(nodes, edges, target_infected, seed=42):
    """Auxiliary function to render the NetworkX graph with pinpoint color accuracy."""
    G = nx.Graph()

    # Mapear nós: os primeiros X nós mudam de cor com base no resultado real da simulação
    for idx, n in enumerate(nodes):
        simulated_state = "infected" if idx < target_infected else "clean"
        G.add_node(n["id"], state=simulated_state)

    for e in edges:
        G.add_edge(e["source"], e["target"])

    color_map = ["#FF4B4B" if data["state"] == "infected" else "#28A745" for _, data in G.nodes(data=True)]

    fig, ax = plt.subplots(figsize=(9, 5))
    pos = nx.spring_layout(G, seed=seed, k=0.3)

    nx.draw(
        G, pos, node_color=color_map, with_labels=False,
        node_size=140, edge_color="#DDDDDD", width=0.8, ax=ax
    )
    return fig


def render_snapshot_breakdown(nodes, target_infected_count):
    """Generates and displays the breakdown table of infected nodes for a specific posture target."""
    st.markdown("#### 📊 Snapshot Breakdown by Department & Hierarchy")

    stats = {}
    for idx, n in enumerate(nodes):
        if idx < target_infected_count:  # Nó considerado infetado neste snapshot
            dept = n.get("department", "General Network")
            level = n.get("hierarchy_level", 1)

            if dept not in stats:
                stats[dept] = {"Level 1 (Staff)": 0, "Level 2 (Managers)": 0, "Level 3 (Directors)": 0}

            label_level = f"Level {level} (" + ("Staff)" if level == 1 else "Managers)" if level == 2 else "Directors)")
            if label_level in stats[dept]:
                stats[dept][label_level] += 1
            else:
                stats[dept][f"Level {level}"] = stats[dept].get(f"Level {level}", 0) + 1

    if stats:
        df_stats = pd.DataFrame.from_dict(stats, orient='index').fillna(0).astype(int)
        st.dataframe(df_stats, use_container_width=True)
    else:
        st.success("🟢 All departments are currently secure. No infected hosts in this snapshot.")


def show():
    st.title("🕸️ Multi-Experiment Network Topology")
    st.markdown("Inspect and compare the structural blast radius across each distinct experimental environment.")

    # 1. Obter a estrutura física original do Grafo (Nós e Arestas do backend)
    graph_data = get_graph()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.warning("⚠️ No base infrastructure compiled. Please initialize your Digital Twin in 'Experiments' first.")
        return

    # Verificação crucial: Se o utilizador ainda não correu o benchmark no Analytics, avisamos
    if "exp1_history" not in st.session_state or not st.session_state.exp1_history:
        st.info(
            "💡 The multi-scenario history is empty. Please go to the 'Analytics' tab and click 'Execute Global Matrix' first to compile the graphs.")
        return

    # Criar 3 Abas na Network View: Uma para cada Grafo de Experiência
    g_tab1, g_tab2, g_tab3 = st.tabs([
        "🛑 Exp 1: Standard Phishing Graph",
        "🎯 Exp 2: Spear Phishing Graph",
        "🔑 Exp 3: Enforced MFA Graph"
    ])

    # Slider temporal global baseado no tamanho real do histórico simulado
    st.divider()
    st.subheader("⏱️ Global Timeline Player")
    total_days = len(st.session_state.exp1_history)
    selected_day = st.slider("Select Simulation Day to visualize across architecture graphs", 1, total_days, total_days)

    # Índice correspondente na lista (Python começa em 0)
    day_index = selected_day - 1

    # ==========================================
    # GRAFO 1: STANDARD PHISHING (DADOS REAIS EXP 1)
    # ==========================================
    with g_tab1:
        st.subheader("Experiment 1 Blast Radius")
        st.caption("Posturing: No MFA, normal cyber awareness. High velocity lateral infection.")

        real_infected_1 = st.session_state.exp1_history[day_index]["total_network_infection"]
        calc_infected_1 = min(real_infected_1, len(nodes))

        fig1 = draw_topology_graph(nodes, edges, calc_infected_1)
        st.pyplot(fig1)
        st.metric("Compromised Workstations (Exp 1)", f"{calc_infected_1} / {len(nodes)} Nodes")

        # CHAMADA CORRIGIDA DA NOVA FUNÇÃO AUXILIAR
        render_snapshot_breakdown(nodes, calc_infected_1)

    # ==========================================
    # GRAFO 2: SPEAR PHISHING (DADOS REAIS EXP 2)
    # ==========================================
    with g_tab2:
        st.subheader("Experiment 2 Blast Radius")
        st.caption("Posturing: Targeted Spear Phishing strike. Severe breach vector, rapid takeover.")

        real_infected_2 = st.session_state.exp2_history[day_index]["total_network_infection"]
        calc_infected_2 = min(real_infected_2, len(nodes))

        fig2 = draw_topology_graph(nodes, edges, calc_infected_2)
        st.pyplot(fig2)

        diff = calc_infected_2 - calc_infected_1
        st.metric("Compromised Workstations (Exp 2)", f"{calc_infected_2} / {len(nodes)} Nodes",
                  f"+{diff} nodes vs Exp 1" if diff >= 0 else f"{diff} nodes")

        # CHAMADA CORRIGIDA DA NOVA FUNÇÃO AUXILIAR
        render_snapshot_breakdown(nodes, calc_infected_2)

    # ==========================================
    # GRAFO 3: SPEAR PHISHING + MFA (DADOS REAIS EXP 3)
    # ==========================================
    with g_tab3:
        st.subheader("Experiment 3 Blast Radius")
        st.caption("Posturing: Cryptographic MFA tokens enforced. Lateral spread effectively contained.")

        real_infected_3 = st.session_state.exp3_history[day_index]["total_network_infection"]
        calc_infected_3 = min(real_infected_3, len(nodes))

        fig3 = draw_topology_graph(nodes, edges, calc_infected_3)
        st.pyplot(fig3)

        mitigated = calc_infected_2 - calc_infected_3
        st.metric("Compromised Workstations (Exp 3)", f"{calc_infected_3} / {len(nodes)} Nodes",
                  f"-{mitigated} nodes mitigated vs Exp 2" if mitigated >= 0 else "", delta_color="normal")

        # CHAMADA CORRIGIDA DA NOVA FUNÇÃO AUXILIAR
        render_snapshot_breakdown(nodes, calc_infected_3)


if __name__ == "__main__":
    show()