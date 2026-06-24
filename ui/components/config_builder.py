import streamlit as st


def build_simulation_config():
    """
    Main dashboard interface for configuring the organization and baseline defenses.
    Threat vectors are omitted visually as they are handled dynamically via benchmarks.
    """

    st.title("🏢 Cyber Digital Twin Configuration")
    st.info("Set up your organization framework and technical defense layers below.")
    st.divider()

    # --- SECTION 1: GENERAL & DEPARTMENTS ---
    st.header("1. Organizational Structure")

    n_depts = st.number_input(
        "Number of Departments",
        min_value=1,
        max_value=20,
        value=2,
        help="Specify how many separate departments exist within the network topography."
    )

    departments = []

    for i in range(int(n_depts)):
        with st.container(border=True):
            st.subheader(f"📍 Department {i + 1}")

            name = st.text_input(
                f"Department Name",
                value=f"Dept_{i + 1}",
                key=f"dept_name_{i}"
            )

            st.caption("Staff Distribution by Hierarchical Level & Education:")

            # Configuração detalhada por Nível Hierárquico
            edu_weights = {"High School": 0.8, "Bachelor's Degree": 1.0, "Master's / PhD": 1.2}

            # --- LEVEL 1 CONFIG ---
            st.markdown("##### **🛠️ Level 1 - Operational Staff**")
            col1_n, col1_ed = st.columns(2)
            with col1_n:
                n_level1 = st.slider("Total Staff (L1)", 1, 100, 5, key=f"n_l1_{i}")
            with col1_ed:
                edu_l1 = st.selectbox("Education (L1)", ["High School", "Bachelor's Degree", "Master's / PhD"], index=1,
                                      key=f"edu_l1_{i}")

            # --- LEVEL 2 CONFIG ---
            st.markdown("##### **💼 Level 2 - Managers / Supervisors**")
            col2_n, col2_ed = st.columns(2)
            with col2_n:
                n_level2 = st.slider("Total Managers (L2)", 0, 20, 1, key=f"n_l2_{i}")
            with col2_ed:
                edu_l2 = st.selectbox("Education (L2)", ["High School", "Bachelor's Degree", "Master's / PhD"], index=1,
                                      key=f"edu_l2_{i}")

            # --- LEVEL 3 CONFIG ---
            st.markdown("##### **👑 Level 3 - Directors / Executives**")
            col3_n, col3_ed = st.columns(2)
            with col3_n:
                n_level3 = st.slider("Total Directors (L3)", 0, 5, 1, key=f"n_l3_{i}")
            with col3_ed:
                edu_l3 = st.selectbox("Education (L3)", ["High School", "Bachelor's Degree", "Master's / PhD"], index=2,
                                      key=f"edu_l3_{i}")

            # --- SOCIAL SETTINGS (Mantém-se partilhado no cluster do departamento) ---
            st.divider()
            st.caption("Departmental Trust Vector Settings:")
            avg_friends = st.slider(
                "Average Close Peer Connections",
                1, 10, 3,
                key=f"friends_{i}",
                help="Specifies how many high-trust social links each employee establishes inside this cluster."
            )

            dept_agents = []
            agent_counter = 1

            # --- GERAR AGENTES LEVEL 1 ---
            edu_mod_l1 = edu_weights[edu_l1]
            for _ in range(n_level1):
                dept_agents.append({
                    "name": f"User_{i + 1}_{agent_counter}",
                    "hierarchy_level": 1,
                    "risk_propensity": 0.5,
                    "awareness_level": min(1.0, 0.5 * edu_mod_l1),  # Aplica escolaridade do L1
                    "education_profile": edu_l1,
                    "trust_links_count": avg_friends
                })
                agent_counter += 1

            # --- GERAR AGENTES LEVEL 2 ---
            edu_mod_l2 = edu_weights[edu_l2]
            for _ in range(n_level2):
                dept_agents.append({
                    "name": f"Manager_{i + 1}_{agent_counter}",
                    "hierarchy_level": 2,
                    "risk_propensity": 0.4,
                    "awareness_level": min(1.0, 0.6 * edu_mod_l2),  # Aplica escolaridade do L2
                    "education_profile": edu_l2,
                    "trust_links_count": avg_friends
                })
                agent_counter += 1

            # --- GERAR AGENTES LEVEL 3 ---
            edu_mod_l3 = edu_weights[edu_l3]
            for _ in range(n_level3):
                dept_agents.append({
                    "name": f"Director_{i + 1}_{agent_counter}",
                    "hierarchy_level": 3,
                    "risk_propensity": 0.3,
                    "awareness_level": min(1.0, 0.7 * edu_mod_l3),  # Aplica escolaridade do L3
                    "education_profile": edu_l3,
                    "trust_links_count": avg_friends
                })
                agent_counter += 1

            departments.append({"name": name, "agents": dept_agents})

    st.divider()

    # --- SECTION 2: DEFENSE MECHANISMS ---
    st.header("2. Mitigation & Defensive Posture")

    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.markdown("**Technical Control**")
        mfa = st.toggle("Enable Multi-Factor Authentication (MFA)", value=False)
    with cd2:
        st.markdown("**Human Control**")
        training = st.slider("Security Awareness Training Effectiveness", 0.0, 1.0, 0.3)
    with cd3:
        st.markdown("**Network Control**")
        segmentation = st.slider("Network Segmentation Level", 0.0, 1.0, 0.5)

    # Dicionário de configuração final pronto a ser enviado para a API do Mesa
    config = {
        "organization": {
            "departments": departments
        },
        "attack": {
            "type": "Phishing",
            "click_rate": 0.5
        },
        "defense": {
            "mfa": mfa,
            "training": training,
            "segmentation": segmentation
        }
    }

    return config