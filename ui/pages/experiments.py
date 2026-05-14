import streamlit as st
# Ajuste nos imports para refletir a nova estrutura
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def show():
    st.title("🧪 Simulation Setup & Experiments")
    st.markdown("""
    Configure aqui os parâmetros da sua organização, o tipo de ataque e as defesas ativas. 
    Estes dados serão enviados para o **Digital Twin Engine** para inicializar o modelo.
    """)

    # 1. Construtor de Configuração
    # Este componente deve retornar o dicionário com 'organization', 'attack' e 'defense'
    config = build_simulation_config()

    st.divider()

    # 2. Botão de Inicialização
    if st.button("🚀 Initialize Digital Twin", use_container_width=True, type="primary"):
        with st.spinner("A enviar configuração para o servidor..."):
            result = start_simulation(config)

            if "error" in result:
                st.error(f"❌ Falha ao iniciar simulação: {result['error']}")
            else:
                st.success("✅ Simulação inicializada com sucesso no backend!")

                # Mostrar um resumo do que foi criado
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Agentes Criados", result.get("agentes", 0))
                with col2:
                    st.metric("Status", "Ready")

                with st.expander("Ver JSON de Resposta"):
                    st.json(result)


# Se o dashboard.py importar este ficheiro
if __name__ == "__main__":
    show()