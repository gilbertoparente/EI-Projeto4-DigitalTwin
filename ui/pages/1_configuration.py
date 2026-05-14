import streamlit as st
import uuid
import requests

st.set_page_config(page_title="Digital Twin Wizard", layout="wide")

st.title("🧠 Digital Twin Configuration Wizard")

# =========================================================
# INIT SESSION STATE
# =========================================================

if "simulation_id" not in st.session_state:
    st.session_state.simulation_id = str(uuid.uuid4())

if "departments" not in st.session_state:
    st.session_state.departments = []

# =========================================================
# STEP 1 — ORGANIZATION
# =========================================================

st.header("🏢 Step 1 — Organização")

org_name = st.text_input("Nome da organização")

num_departments = st.number_input(
    "Número inicial de departamentos",
    min_value=1,
    max_value=20,
    value=3
)

if st.button("➕ Gerar estrutura de departamentos"):
    st.session_state.departments = []

    for i in range(num_departments):
        st.session_state.departments.append({
            "name": f"Department {i+1}",
            "type": "General",
            "agents": []
        })

st.divider()

# =========================================================
# STEP 2 — DEPARTMENTS BUILDER
# =========================================================

st.header("🏢 Step 2 — Departamentos")

for i, dept in enumerate(st.session_state.departments):

    with st.expander(f"📁 {dept['name']}", expanded=True):

        dept_name = st.text_input(
            "Nome do departamento",
            value=dept["name"],
            key=f"dept_name_{i}"
        )

        dept_type = st.selectbox(
            "Tipo de departamento",
            ["IT", "Finance", "HR", "Operations", "General"],
            key=f"dept_type_{i}"
        )

        num_agents = st.number_input(
            "Número de agentes",
            min_value=1,
            max_value=50,
            value=max(len(dept["agents"]), 3),
            key=f"num_agents_{i}"
        )

        # update dept base info
        dept["name"] = dept_name
        dept["type"] = dept_type

        # =====================================================
        # AGENTS GENERATION
        # =====================================================

        if st.button(f"👤 Gerar agentes para {dept_name}", key=f"gen_agents_{i}"):

            dept["agents"] = []

            for j in range(num_agents):
                dept["agents"].append({
                    "id": str(uuid.uuid4()),
                    "name": f"Agent_{i}_{j}",
                    "education": "BSc",
                    "risk_propensity": 0.5,
                    "awareness_level": 0.5,
                    "hierarchy_level": j
                })

        # =====================================================
        # AGENT EDITOR
        # =====================================================

        for j, agent in enumerate(dept["agents"]):

            with st.container():

                st.markdown(f"**👤 Agent {j+1}**")

                agent["name"] = st.text_input(
                    "Nome",
                    value=agent["name"],
                    key=f"name_{i}_{j}"
                )

                agent["education"] = st.selectbox(
                    "Escolaridade",
                    ["Basic", "HighSchool", "BSc", "MSc", "PhD"],
                    index=2,
                    key=f"edu_{i}_{j}"
                )

                agent["risk_propensity"] = st.slider(
                    "Risco",
                    0.0, 1.0,
                    value=agent["risk_propensity"],
                    key=f"risk_{i}_{j}"
                )

                agent["awareness_level"] = st.slider(
                    "Awareness",
                    0.0, 1.0,
                    value=agent["awareness_level"],
                    key=f"aware_{i}_{j}"
                )

st.divider()

# =========================================================
# STEP 3 — GLOBAL SETTINGS
# =========================================================

st.header("💣 Step 3 — Ataques & Defesa")

attack_type = st.selectbox(
    "Tipo de ataque",
    ["Phishing", "Spear Phishing"]
)

open_rate = st.slider("Taxa de abertura", 0.0, 1.0, 0.3)
click_rate = st.slider("Taxa de clique", 0.0, 1.0, 0.2)
submit_rate = st.slider("Taxa de submissão", 0.0, 1.0, 0.1)

st.subheader("🛡️ Defesa")

mfa = st.checkbox("MFA", value=True)
training = st.slider("Formação", 0.0, 1.0, 0.5)
segmentation = st.slider("Segmentação", 0.0, 1.0, 0.5)

st.divider()

# =========================================================
# RELATIONSHIP PLACEHOLDER (SIMPLIFIED FOR NOW)
# =========================================================

st.header("🔗 Step 4 — Relações (simplificado)")

relation_mode = st.selectbox(
    "Tipo de relações",
    ["Auto-generate", "Manual (future)"]
)

st.info("Relações serão geradas automaticamente no backend com base em confiança e departamento.")

st.divider()

# =========================================================
# EXPORT JSON
# =========================================================

st.header("📦 Configuração Final")

config = {
    "simulation_id": st.session_state.simulation_id,
    "organization": {
        "name": org_name,
        "departments": st.session_state.departments
    },
    "attack": {
        "type": attack_type,
        "open_rate": open_rate,
        "click_rate": click_rate,
        "submit_rate": submit_rate
    },
    "defense": {
        "mfa": mfa,
        "training": training,
        "segmentation": segmentation
    }
}

st.json(config)

# =========================================================
# EXECUTE
# =========================================================

if st.button("🚀 Executar Simulação"):

    try:
        response = requests.post(
            "http://127.0.0.1:8000/start",
            json=config
        )

        st.success("Simulação enviada com sucesso!")
        st.json(response.json())

    except Exception as e:
        st.error(f"Erro: {e}")