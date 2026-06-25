import streamlit as st
import pandas as pd
from ui.api_client import step_simulation, get_status, get_graph


def show():
    st.title("🟢 Live System Monitor")
    st.markdown("Real-time telemetry of network nodes, topological state changes, and active threat propagation.")

    # 1. Fetching current engine telemetry
    status = get_status()

    if "error" in status or status.get("status") == "idle":
        st.warning(
            "⚠️ The Simulation Engine is offline or has not been compiled yet. Please initialize your architecture in 'Experiments'.")
        return

    # Metric layout cards at the header
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Network Nodes", status.get("agents", 0))
    m2.metric("Current Timeline Age", f"Day {status.get('tick', 0)}")

    # 2. Timeline Controls & Topology Layout split
    col_ctrl, col_graph = st.columns([2, 3])

    with col_ctrl:
        st.subheader("⏱️ Timeline Controls")

        # Execution strategy selection
        run_mode = st.radio("Execution Strategy", ["Manual (Step-by-Step)", "Automatic (Full Run)"], horizontal=True)

        if run_mode == "Manual (Step-by-Step)":
            st.caption("Advance the social engineering campaign timeline by exactly 1 single unit (Tick/Day).")
            if st.button("▶️ Advance 1 Single Step", use_container_width=True, type="primary"):
                execute_steps(1)
        else:
            st.caption("Execute a sequence of days automatically until the malware vector stabilizes.")
            steps_to_run = st.slider("Timeline Horizon (Days to simulate)", 5, 30, 10)
            if st.button(f"🚀 Trigger Automated Run ({steps_to_run} Days)", use_container_width=True, type="primary"):
                execute_steps(steps_to_run)

    with col_graph:
        st.subheader("🕸️ Topology Saturation")
        graph_data = get_graph()

        # Security constraint verification for graph metadata
        if isinstance(graph_data, dict) and "nodes" in graph_data and graph_data["nodes"]:
            total_nodes = len(graph_data["nodes"])
            infected_count = sum(1 for n in graph_data["nodes"] if n.get("state") in ["infected", "compromised"])

            st.info(f"Active communication fabric containing {total_nodes} live routing agents.")

            # Progress bar indicating the structural blast radius of the phishing strike
            saturation_ratio = infected_count / total_nodes if total_nodes > 0 else 0.0
            st.progress(saturation_ratio,
                        text=f"Blast Radius Saturation: {infected_count} / {total_nodes} agents compromised")
        else:
            st.warning("Awaiting initial topological graph sync...")
            st.caption("Make sure you have deployed the simulation instance inside the blueprint configuration tab.")


def execute_steps(num_steps):
    """Auxiliary internal loop engine to execute sequential steps and store metrics telemetry."""
    # Initialize global history in session if it doesn't exist
    if "history" not in st.session_state:
        st.session_state.history = []

    with st.spinner(f"Simulating {num_steps} operational loops in background..."):
        for _ in range(num_steps):
            data = step_simulation()
            if "error" in data:
                st.error(f"Execution Error: {data['error']}")
                break
            elif "result" not in data:
                st.warning("The model state was flushed. Please redeploy in Experiments.")
                break
            else:
                entry = data["result"]
                entry["tick"] = data["tick"]

                # Logic correction: map 'compromised' to 'infected' for visualization consistency
                if "compromised" in entry and "infected" not in entry:
                    entry["infected"] = entry["compromised"]
                elif "infected" not in entry:
                    entry["infected"] = 0

                # Capture total network accumulation
                entry["total_network_infection"] = data.get("total_compromised", 0)

                st.session_state.history.append(entry)

        st.success(f"Successfully processed {num_steps} simulation ticks!")
        st.rerun()


if __name__ == "__main__":
    show()