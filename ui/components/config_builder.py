import streamlit as st


def build_simulation_config():
    """
    Interface com opções globais na sidebar e configuração
    detalhada dos departamentos no centro da página.
    """

    # --- SIDEBAR: OPÇÕES GLOBAIS ---
    st.sidebar.header("⚙️ Opções Gerais")

    # Limite de 20 Departamentos
    n_depts = st.sidebar.number_input(
        "Número de Departamentos",
        min_value=1,
        max_value=20,
        value=2
    )

    st.sidebar.divider()

    # Configuração das Defesas na Sidebar para libertar espaço no centro
    st.sidebar.subheader("🛡️ Medidas de Defesa")
    mfa = st.sidebar.toggle("Ativar MFA", value=False)
    training = st.sidebar.slider("Eficácia da Formação", 0.0, 1.0, 0.3)
    segmentation = st.sidebar.slider("Nível de Segmentação", 0.0, 1.0, 0.5)

    # --- CENTRO DA PÁGINA: DEPARTAMENTOS E ATAQUE ---
    st.title("🏢 Configuração da Organização")
    st.info("Configure os detalhes de cada departamento abaixo.")

    departments = []

    # Criar colunas ou usar expanders no centro para os departamentos
    for i in range(int(n_depts)):
        with st.container(border=True):  # Dá um aspeto de "card" a cada departamento
            st.subheader(f"📍 Departamento {i + 1}")

            col_name, col_agents = st.columns([2, 3])

            with col_name:
                name = st.text_input(
                    f"Nome do Departamento",
                    value=f"Dept_{i + 1}",
                    key=f"dept_name_{i}"
                )

            with col_agents:
                # Limite de 100 Agentes
                n_agents = st.slider(
                    f"Quantidade de Agentes",
                    1, 100, 5,
                    key=f"n_agents_slider_{i}"
                )

            # Expander para não ocupar demasiado espaço vertical com muitos agentes
            with st.expander(f"👤 Configurar Níveis dos Agentes ({n_agents})"):
                dept_agents = []
                for j in range(n_agents):
                    unique_key = f"hier_dept_{i}_agent_{j}"

                    # Usar colunas dentro do expander para ser mais compacto
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.caption(f"User {j + 1}")
                    with c2:
                        level = st.select_slider(
                            f"Nível",
                            options=[1, 2, 3],
                            value=1,
                            key=unique_key,
                            label_visibility="collapsed"  # Esconde o texto para poupar espaço
                        )

                    dept_agents.append({
                        "name": f"User_{i + 1}_{j + 1}",
                        "hierarchy_level": level,
                        "risk_propensity": 0.5,
                        "awareness_level": 0.5
                    })

            departments.append({"name": name, "agents": dept_agents})

    st.divider()

    # Configuração do Ataque no Centro (Final da página)
    st.header("⚔️ Parâmetros de Ataque")
    ca1, ca2 = st.columns(2)
    with ca1:
        attack_type = st.selectbox("Tipo de Ataque", ["Phishing", "Spear Phishing"])
    with ca2:
        click_rate = st.slider("Intensidade do Ataque (Base)", 0.0, 1.0, 0.5)

    # Montar o dicionário final
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