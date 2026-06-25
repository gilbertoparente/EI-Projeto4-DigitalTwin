import streamlit as st
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def show():
    st.title("🧪 Simulation Setup & Experiments")
    st.markdown("""
    Configure your organization framework, threat vectors, and mitigation levels below. 
    This blueprint will be transmitted to the **Digital Twin Engine** to compile the stochastic model graph.
    """)

    # 1. Configuration Builder
    config = build_simulation_config()

    st.divider()

    # 2. Initialization Button
    if st.button("🚀 Initialize Digital Twin Engine", use_container_width=True, type="primary"):
        with st.spinner("Transmitting architecture to simulation cluster..."):
            result = start_simulation(config)

            if "error" in result:
                st.error(f"❌ Failed to initialize simulation state: {result['error']}")
            else:
                st.success("✅ Digital Twin compiled and mapped successfully onto backend environment!")

                # CRITICAL CHANGE: Only store config in session state if API success
                st.session_state["current_config"] = config

                # Summary of metrics returned by the API
                col1, col2 = st.columns(2)
                with col1:
                    # Attempting to read 'agents' from the API response
                    total_agents = result.get("agents", 0)
                    st.metric("Total Compiled Agents", total_agents)
                with col2:
                    st.metric("Engine Runtime Status", "Ready")

                with st.expander("Inspect JSON Architecture Payload"):
                    st.json(result)


if __name__ == "__main__":
    show()