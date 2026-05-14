import streamlit as st


def build_simulation_config():
    """
    Cria a interface visual para configurar a simulação e
    retorna um dicionário com todos os parâmetros.
    """
    st.sidebar.header("🏢 Configuração da Organização")

    # Configuração de Departamentos
    n_depts = st.sidebar.number_input("Número de Departamentos", min_value=1, max_value=5, value=2)

    departments = []
    for i in range(n_depts):
        with st.sidebar.expander(f"Departamento {i + 1}"):
            # Adicionada key única para o nome do departamento
            name = st.text_input(f"Nome do Dept {i + 1}", value=f"Dept_{i + 1}", key=f"dept_name_{i}")
            n_agents = st.slider(f"Número de Agentes (Dept {i + 1})", 2, 20, 5, key=f"n_agents_slider_{i}")

            dept_agents = []
            for j in range(n_agents):
                # KEY ÚNICA: combina o index do departamento (i) com o do agente (j)
                unique_key = f"hier_dept_{i}_agent_{j}"

                dept_agents.append({
                    "name": f"User_{i + 1}_{j + 1}",
                    "hierarchy_level": st.select_slider(
                        f"Nível Hierárquico {j + 1}",
                        options=[1, 2, 3],
                        value=1,
                        key=unique_key  # Isto resolve o erro!
                    ),
                    "risk_propensity": 0.5,
                    "awareness_level": 0.5
                })

            departments.append({"name": name, "agents": dept_agents})

    # Configuração do Ataque
    st.header("⚔️ Parâmetros de Ataque")
    col1, col2 = st.columns(2)
    with col1:
        attack_type = st.selectbox("Tipo de Ataque", ["Phishing", "Spear Phishing"])
    with col2:
        click_rate = st.slider("Intensidade do Ataque (Base)", 0.0, 1.0, 0.5)

    # Configuração das Defesas (Mitigações)
    st.header("🛡️ Medidas de Defesa")
    c1, c2, c3 = st.columns(3)
    with c1:
        mfa = st.toggle("Ativar MFA", value=True)
    with c2:
        training = st.slider("Eficácia da Formação", 0.0, 1.0, 0.3)
    with c3:
        segmentation = st.slider("Nível de Segmentação", 0.0, 1.0, 0.5)

    # Montar o dicionário final que a API espera receber
    config = {
        "organization": {
            "departments": departments
        },
        "attack": {
            "type": attack_type,
            "click_rate": click_rate
        },
        "defense": {
            "mfa": mfa,
            "training": training,
            "segmentation": segmentation
        }
    }

    return config