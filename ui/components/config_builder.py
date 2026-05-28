import streamlit as st


def _tip(label: str, tooltip: str):
    """Renders a label with a ? tooltip button inline."""
    col_l, col_q = st.columns([8, 1])
    with col_l:
        st.markdown(f"<p style='margin:0; font-size:14px; font-weight:500; color:#c9d1d9'>{label}</p>",
                    unsafe_allow_html=True)
    with col_q:
        st.markdown(
            f"""<div title="{tooltip}" style="
                display:inline-flex; align-items:center; justify-content:center;
                width:20px; height:20px; border-radius:50%;
                border:1px solid #484f58; color:#8b949e;
                font-size:11px; font-weight:700; cursor:help;
                margin-top:2px;">?</div>""",
            unsafe_allow_html=True
        )


def build_simulation_config() -> dict:
    """
    Builds the full simulation config dict from the main-area form.
    Organisation section is rendered inline (not in sidebar).
    """

    # ── Section 1: Organisation ───────────────────────────────
    st.markdown("""
    <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                padding:1.25rem 1.5rem; margin-bottom:1rem;">
      <div style="font-size:13px; font-weight:600; color:#58a6ff;
                  text-transform:uppercase; letter-spacing:.06em; margin-bottom:1rem;">
        🏢 Organização
      </div>
    """, unsafe_allow_html=True)

    n_depts = st.number_input(
        "Número de departamentos",
        min_value=1, max_value=6, value=2,
        help="Quantos departamentos distintos terá a organização simulada."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    departments = []
    for i in range(int(n_depts)):
        with st.expander(f"Departamento {i + 1}", expanded=(i == 0)):
            c1, c2 = st.columns([2, 1])
            with c1:
                name = st.text_input("Nome do departamento",
                                     value=f"Dept_{i + 1}",
                                     key=f"dept_name_{i}")
            with c2:
                n_agents = st.number_input("Nº de agentes",
                                           min_value=2, max_value=50, value=5,
                                           key=f"n_agents_{i}")

            dept_agents = []
            if n_agents > 0:
                st.markdown("<p style='font-size:12px;color:#6e7681;margin:8px 0 4px'>Perfil dos agentes</p>",
                            unsafe_allow_html=True)
                a1, a2, a3 = st.columns(3)
                with a1:
                    risk = st.slider("Propensão ao risco",
                                     0.0, 1.0, 0.5, 0.05,
                                     key=f"risk_{i}",
                                     help="Probabilidade base de um agente clicar numa mensagem suspeita.")
                with a2:
                    awareness = st.slider("Nível de consciência",
                                          0.0, 1.0, 0.5, 0.05,
                                          key=f"aware_{i}",
                                          help="Literacia em cibersegurança. Valores altos reduzem a taxa de clique.")
                with a3:
                    hier = st.select_slider("Nível hierárquico",
                                            options=[1, 2, 3],
                                            value=1,
                                            key=f"hier_{i}",
                                            help="1 = operacional, 2 = gestão intermédia, 3 = direção.")

                for j in range(int(n_agents)):
                    dept_agents.append({
                        "name": f"User_{i+1}_{j+1}",
                        "hierarchy_level": hier,
                        "risk_propensity": risk,
                        "awareness_level": awareness,
                    })

            departments.append({"name": name, "agents": dept_agents})

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Section 2: Attack ─────────────────────────────────────
    st.markdown("""
    <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                padding:1.25rem 1.5rem; margin-bottom:1rem;">
      <div style="font-size:13px; font-weight:600; color:#f78166;
                  text-transform:uppercase; letter-spacing:.06em; margin-bottom:1rem;">
        ⚔️ Ataque
      </div>
    """, unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)
    with ac1:
        attack_type = st.selectbox(
            "Tipo de ataque",
            ["Phishing", "Spear Phishing"],
            help="Phishing: campanha massiva aleatória. Spear Phishing: ataque direcionado aos agentes com hierarquia mais alta."
        )
    with ac2:
        click_rate = st.slider(
            "Intensidade base do ataque",
            0.0, 1.0, 0.5, 0.05,
            help="Escala a probabilidade de sucesso inicial do atacante antes das defesas serem aplicadas."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section 3: Defense ────────────────────────────────────
    st.markdown("""
    <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                padding:1.25rem 1.5rem; margin-bottom:1.5rem;">
      <div style="font-size:13px; font-weight:600; color:#3fb950;
                  text-transform:uppercase; letter-spacing:.06em; margin-bottom:1rem;">
        🛡️ Defesas
      </div>
    """, unsafe_allow_html=True)

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.markdown("**MFA**", unsafe_allow_html=False)
        mfa = st.toggle(
            "Ativar MFA",
            value=True,
            help="Multi-Factor Authentication. Bloqueia ~90% das tentativas de acesso mesmo após credenciais comprometidas."
        )
    with dc2:
        training = st.slider(
            "Eficácia da formação",
            0.0, 1.0, 0.3, 0.05,
            help="Simula programas de awareness. Aumenta o nível de consciência dos agentes a cada tick."
        )
    with dc3:
        segmentation = st.slider(
            "Segmentação de rede",
            0.0, 1.0, 0.5, 0.05,
            help="0 = rede plana (lateral movement livre). 1 = zero-trust (propagação entre departamentos bloqueada)."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "organization": {"departments": departments},
        "attack":       {"type": attack_type, "click_rate": click_rate},
        "defense":      {"mfa": mfa, "training": training, "segmentation": segmentation},
    }
