import streamlit as st
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def show():
    # Traduzido para Inglês para consistência com o resto do Dashboard
    st.title("🧪 Simulation Setup & Experiments")
    st.markdown("""
    Configure your organization framework, threat vectors, and mitigation levels below. 
    This blueprint will be transmitted to the **Digital Twin Engine** to compile the stochastic model graph.
    """)

    # 1. Construtor de Configuração (que já traduzimos para Inglês)
    config = build_simulation_config()

    st.divider()

    # 2. Botão de Inicialização (Corrigido use_container_width -> width="stretch")
    if st.button("🚀 Initialize Digital Twin Engine", width="stretch", type="primary"):
        with st.spinner("Transmitting architecture to simulation cluster..."):
            result = start_simulation(config)

            if "error" in result:
                st.error(f"❌ Failed to initialize simulation state: {result['error']}")
            else:
                st.success("✅ Digital Twin compiled and mapped successfully onto backend environment!")

                # MUDANÇA CRUCIAL AQUI: Só guarda a config na sessão se a API aceitou com sucesso
                st.session_state["current_config"] = config

                # Resumo rápido em Inglês das métricas devolvidas pela API
                col1, col2 = st.columns(2)
                with col1:
                    # Tenta ler 'agents' ou o teu campo 'agentes' vindo da API
                    total_agents = result.get("agents", result.get("agentes", 0))
                    st.metric("Total Compiled Agents", total_agents)
                with col2:
                    st.metric("Engine Runtime Status", "Ready")

                with st.expander("Inspect JSON Architecture Payload"):
                    st.json(result)


if __name__ == "__main__":
    show()