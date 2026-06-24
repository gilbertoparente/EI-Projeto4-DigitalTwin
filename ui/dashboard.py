import streamlit as st

# 1. Global Page Configuration
st.set_page_config(
    page_title="Cyber Digital Twin | IPVC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS to hide native navigation and tune metrics
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
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

# 3. Sidebar - Clean Navigation Area Only
with st.sidebar:
    try:
        st.image("https://www.ipvc.pt/wp-content/uploads/2020/12/logo-ipvc.png", width="stretch")
    except:
        st.subheader("🏫 IPVC")

    st.title("🛡️ CyberTwin Panel")
    st.caption("Digital Twin for Social Engineering Simulation")
    st.divider()

    # Radio Selection in English
    page = st.radio(
        "Main Navigation",
        [
            "🧪 Experiments",
            "🟢 Live System",
            "📊 Analytics",
            "🕸️ Network View"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.info(
        "💡 **Quick Tip:** Build and initialize your scenario in *Experiments* before running simulation steps in *Live System*.")
    st.caption("Cybersecurity Project @ IPVC 2026")

# 4. Dynamic Page Routing
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