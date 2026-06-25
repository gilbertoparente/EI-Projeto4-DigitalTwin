import streamlit as st


EDUCATION_LEVELS = ["High School", "Bachelor's Degree", "Master's / PhD"]


def build_simulation_config():
    st.title("Cyber Digital Twin Configuration")
    st.info("Set up your organization, attack model, and defensive posture.")
    st.divider()

    st.header("1. Scientific Model Parameters")
    with st.expander("Manual calibration", expanded=True):
        st.markdown(
            """
            **Generic Phishing:** P(click) = global_intensity x (1 - global_training)

            **Spear Phishing:** P(click) = min(1.0, global_intensity + spear_bonus)

            **Individual Situational Awareness:** awareness = role_base x education_profile

            **Social Homophily Bias:** if the email source is a trusted node, P(click) = P(click) x homophily_multiplier
            """
        )

        attack_col, role_col, edu_col = st.columns(3)
        with attack_col:
            st.subheader("Attack Formula")
            global_intensity = st.slider("global_intensity", 0.0, 1.0, 0.5)
            global_training = st.slider("global_training", 0.0, 1.0, 0.3)
            spear_bonus = st.slider("spear_bonus", 0.0, 1.0, 0.2)
            homophily_multiplier = st.slider("homophily_multiplier", 1.0, 5.0, 2.0)

        with role_col:
            st.subheader("role_base")
            w_l1 = st.slider("Role base L1", 0.0, 1.0, 0.5)
            w_l2 = st.slider("Role base L2", 0.0, 1.0, 0.6)
            w_l3 = st.slider("Role base L3", 0.0, 1.0, 0.7)

        with edu_col:
            st.subheader("education_profile")
            edu_hs = st.slider("High School", 0.0, 2.0, 0.8)
            edu_ba = st.slider("Bachelor's Degree", 0.0, 2.0, 1.0)
            edu_ma = st.slider("Master's / PhD", 0.0, 2.0, 1.2)

    weights = {
        "cargo": {1: w_l1, 2: w_l2, 3: w_l3},
        "edu": {
            "High School": edu_hs,
            "Bachelor's Degree": edu_ba,
            "Master's / PhD": edu_ma,
        },
    }

    generic_probability = global_intensity * (1 - global_training)
    spear_probability = min(1.0, global_intensity + spear_bonus)
    m1, m2, m3 = st.columns(3)
    m1.metric("Generic phishing P(click)", f"{generic_probability:.2f}")
    m2.metric("Spear phishing P(click)", f"{spear_probability:.2f}")
    m3.metric("Trusted-link multiplier", f"x{homophily_multiplier:.1f}")

    st.header("2. Attack Selection")
    attack_type = st.radio("Attack type", ["Phishing", "Spear Phishing"], horizontal=True)

    st.header("3. Organizational Structure")
    n_depts = st.number_input("Number of Departments", min_value=1, max_value=20, value=2)
    departments = []

    for i in range(int(n_depts)):
        with st.container(border=True):
            name = st.text_input(f"Department {i + 1} Name", value=f"Dept_{i + 1}", key=f"d_{i}")
            n_l1, n_l2, n_l3 = st.columns(3)
            num1 = n_l1.number_input("Staff L1", 1, 100, 5, key=f"n1_{i}")
            num2 = n_l2.number_input("Managers L2", 0, 20, 1, key=f"n2_{i}")
            num3 = n_l3.number_input("Directors L3", 0, 5, 1, key=f"n3_{i}")

            edu_l1 = st.selectbox("Education L1", EDUCATION_LEVELS, index=1, key=f"edu1_{i}")
            edu_l2 = st.selectbox("Education L2", EDUCATION_LEVELS, index=1, key=f"edu2_{i}")
            edu_l3 = st.selectbox("Education L3", EDUCATION_LEVELS, index=2, key=f"edu3_{i}")
            avg_friends = st.slider("trust_links_count", 1, 10, 3, key=f"friends_{i}")

            dept_agents = []
            agent_counter = 1

            for _ in range(int(num1)):
                dept_agents.append(_make_agent(i, agent_counter, "User", 1, 0.5, edu_l1, avg_friends, weights))
                agent_counter += 1

            for _ in range(int(num2)):
                dept_agents.append(_make_agent(i, agent_counter, "Manager", 2, 0.4, edu_l2, avg_friends, weights))
                agent_counter += 1

            for _ in range(int(num3)):
                dept_agents.append(_make_agent(i, agent_counter, "Director", 3, 0.3, edu_l3, avg_friends, weights))
                agent_counter += 1

            departments.append({"name": name, "agents": dept_agents})

    st.header("4. Defensive Posture")
    defense_col1, defense_col2, defense_col3 = st.columns(3)
    with defense_col1:
        training_coverage = st.slider("Training coverage", 0.0, 1.0, 0.0)
    with defense_col2:
        mfa = st.toggle("Enable MFA", value=False)
    with defense_col3:
        seg = st.slider("Network Segmentation", 0.0, 1.0, 0.5)

    return {
        "organization": {"departments": departments},
        "scientific_params": weights,
        "attack": {"type": attack_type},
        "defense": {
            "mfa": mfa,
            "training": global_training,
            "training_coverage": training_coverage,
            "segmentation": seg,
        },
        "attack_params": {
            "global_intensity": global_intensity,
            "global_training": global_training,
            "spear_bonus": spear_bonus,
            "homophily_multiplier": homophily_multiplier,
            "role_base": weights["cargo"],
            "education_profile": weights["edu"],
        },
    }


def _make_agent(dept_index, agent_counter, prefix, level, risk, education, trust_links, weights):
    awareness = min(1.0, weights["cargo"][level] * weights["edu"][education])
    return {
        "name": f"{prefix}_{dept_index + 1}_{agent_counter}",
        "hierarchy_level": level,
        "risk_propensity": risk,
        "awareness_level": awareness,
        "education_level": education,
        "education": education,
        "trust_links_count": trust_links,
    }