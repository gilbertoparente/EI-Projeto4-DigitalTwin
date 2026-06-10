import streamlit as st
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def _section_heading(label: str, color: str = "#58a6ff"):
    st.markdown(
        f"""<div style="border-left:3px solid {color}; padding-left:12px; margin-bottom:.75rem;">
              <span style="font-size:11px; font-weight:600; color:{color};
                           text-transform:uppercase; letter-spacing:.06em;">{label}</span>
            </div>""",
        unsafe_allow_html=True,
    )


def _alert(msg: str, kind: str = "info"):
    styles = {
        "success": ("#0d2b1d", "#1a6e2d", "#3fb950", "ti-check"),
        "error":   ("#3d0f0f", "#7a2020", "#f85149", "ti-x"),
        "warning": ("#2a1700", "#5a3500", "#e3b341", "ti-alert-triangle"),
        "info":    ("#1a2a4a", "#2d5096", "#58a6ff", "ti-info-circle"),
    }
    bg, border, color, icon = styles.get(kind, styles["info"])
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:10px;background:{bg};
                        border:1px solid {border};border-radius:8px;padding:10px 14px;margin:.5rem 0;">
              <i class="ti {icon}" style="color:{color};font-size:16px;flex-shrink:0" aria-hidden="true"></i>
              <span style="color:{color};font-size:13px;">{msg}</span>
            </div>
            <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css">""",
        unsafe_allow_html=True,
    )


def show():
    st.markdown("""
    <h1 style='margin-bottom:.25rem'>Experiments</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Configure a organização, o vetor de ataque e as defesas antes de inicializar o Digital Twin.
    </p>
    """, unsafe_allow_html=True)

    config = build_simulation_config()

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        launch = st.button(
            "Inicializar Digital Twin",
            use_container_width=True,
            type="primary",
        )
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
            _alert(f"Falha ao iniciar simulação: {result['error']}", "error")
        else:
            _alert("Simulação inicializada com sucesso!", "success")
            m1, m2, m3 = st.columns(3)
            m1.metric("Agentes criados", result.get("agentes", 0))
            m2.metric("Tipo de ataque",  config["attack"]["type"])
            m3.metric("MFA",             "Ativo" if config["defense"]["mfa"] else "Inativo")

            with st.expander("Ver resposta JSON do servidor"):
                st.json(result)