import streamlit as st
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def show():
    st.markdown("""
    <h1 style='margin-bottom:.25rem'>⚗️ Experiments</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Configure a organização, o vetor de ataque e as defesas antes de inicializar o Digital Twin.
    </p>
    """, unsafe_allow_html=True)

    config = build_simulation_config()

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        launch = st.button("🚀 Inicializar Digital Twin",
                           use_container_width=True,
                           type="primary")
    with col_info:
        total_agents = sum(
            len(d["agents"]) for d in config["organization"]["departments"]
        )
        st.markdown(
            f"<p style='color:#6e7681; font-size:13px; margin-top:.6rem'>"
            f"Pronto para criar <strong style='color:#e6edf3'>{total_agents} agentes</strong> "
            f"em <strong style='color:#e6edf3'>"
            f"{len(config['organization']['departments'])} departamento(s)</strong>.</p>",
            unsafe_allow_html=True
        )

    if launch:
        with st.spinner("A enviar configuração para o servidor..."):
            result = start_simulation(config)

        if "error" in result:
            st.error(f"❌ Falha ao iniciar simulação: {result['error']}")
        else:
            st.success("✅ Simulação inicializada com sucesso!")
            m1, m2, m3 = st.columns(3)
            m1.metric("Agentes criados", result.get("agentes", 0))
            m2.metric("Tipo de ataque",  config["attack"]["type"])
            m3.metric("MFA",             "Ativo" if config["defense"]["mfa"] else "Inativo")

            with st.expander("Ver resposta JSON do servidor"):
                st.json(result)
