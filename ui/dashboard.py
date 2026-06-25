import streamlit as st


st.set_page_config(
    page_title="Cyber Digital Twin | IPVC",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    .main { background-color: #f5f7f9; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.subheader("IPVC")
    st.title("CyberTwin Panel")
    st.caption("Digital Twin for Social Engineering Simulation")
    st.divider()

    page = st.radio(
        "Main Navigation",
        ["Experiments", "Live System", "Analytics", "Network View"],
        label_visibility="collapsed",
    )

    st.divider()
    st.info("Build and initialize the scenario in Experiments before running the Live System.")
    st.caption("Cybersecurity Project @ IPVC 2026")


if page == "Experiments":
    from ui.pages import experiments

    experiments.show()
elif page == "Live System":
    from ui.pages import live_system

    live_system.show()
elif page == "Analytics":
    from ui.pages import analytics

    analytics.show()
elif page == "Network View":
    from ui.pages import network

    network.show()