import streamlit as st
import time
# Imports atualizados para a nova estrutura
from ui.api_client import step_simulation, get_status, get_graph


def show():
    st.title("🟢 Live System Monitor")
    st.markdown("Monitorização em tempo real do estado dos agentes e propagação de ameaças.")

    # 1. Cabeçalho de Métricas (Dashboard Rápido)
    status = get_status()

    if "error" in status or status.get("status") == "idle":
        st.warning("⚠️ O sistema está offline ou a simulação ainda não foi iniciada.")
        return

    # Layout de métricas em colunas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Agents", status.get("agents", 0))
    # Note: No seu SimulationService, estas métricas estão dentro de listas no dict 'metrics'
    m2.metric("Tick Atual", status.get("tick", 0))

    st.divider()

    # 2. Controlo e Execução
    col_ctrl, col_graph = st.columns([1, 2])

    with col_ctrl:
        st.subheader("Controls")
        if st.button("🚀 Run Simulation Step", use_container_width=True, type="primary"):
            with st.spinner("A processar tick..."):
                data = step_simulation()
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success(f"Tick {data['tick']} concluído!")
                    st.json(data["result"])

    with col_graph:
        st.subheader("Network Topology")
        graph_data = get_graph()

        # VERIFICAÇÃO DE SEGURANÇA:
        # Se graph_data for um erro ou não tiver a chave 'nodes', mostramos um aviso
        if isinstance(graph_data, dict) and "nodes" in graph_data and graph_data["nodes"]:
            st.info(f"Rede com {len(graph_data['nodes'])} nós.")
            infected_count = sum(1 for n in graph_data["nodes"] if n["state"] == "infected")
            st.progress(infected_count / len(graph_data["nodes"]), text=f"Infeção: {infected_count} agentes")
        else:
            st.warning("Aguardando inicialização da rede...")
            st.caption("Vá a 'Experiments' e clique em 'Initialize' primeiro.")


if __name__ == "__main__":
    show()