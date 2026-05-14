import streamlit as st

# 1. Configuração Global da Página (Deve ser sempre o primeiro comando Streamlit)
st.set_page_config(
    page_title="Cyber Digital Twin | IPVC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilização Customizada (Opcional, para um look mais "Cyber")
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar de Navegação
with st.sidebar:
    st.image("https://www.ipvc.pt/wp-content/uploads/2020/12/logo-ipvc.png", width=150)  # Exemplo de logo
    st.title("🛡️ CyberTwin Panel")
    st.info("Digital Twin para Simulação de Engenharia Social")

    page = st.radio("Navegação Principal", [
        "🧪 Experiments",
        "🟢 Live System",
        "📊 Analytics",
        "🕸️ Network View"
    ])

    st.divider()
    st.caption("Desenvolvido para Projeto de Cibersegurança @ IPVC")

# 4. Encaminhamento de Páginas
# Removemos o 'from ui.pages.X import *' e usamos chamadas explícitas à função show()
if "Experiments" in page:
    from ui.pages import experiments

    experiments.show()

elif "Live System" in page:
    from ui.pages import live_system

    live_system.show()

elif "Analytics" in page:
    from ui.pages import analytics

    analytics.show()

elif "Network View" in page:
    from ui.pages import network

    network.show()