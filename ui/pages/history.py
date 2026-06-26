import pandas as pd
import streamlit as st
from ui.api_client import get_history, get_history_steps


def show():
    st.title("📜 Simulation History")
    st.markdown("Browse and compare past runs stored in the Digital Twin database.")

    data = get_history()
    runs = data.get("runs", [])

    if not runs:
        st.info("No simulations found in history. Run some experiments first!")
        return

    for run in runs:
        run_id     = run["id"]
        timestamp  = run["timestamp"]
        experiment = run["experiment_type"]
        attack     = run["attack_type"]
        total_comp = run["total_compromised"]
        num_agents = run["num_agents"]
        config_data= run["config"]
        graph_data = run.get("graph", {})
        mfa        = run.get("mfa_enabled", False)
        training   = run.get("training_level", 0)
        seg        = run.get("segmentation_level", 0.5)

        title = f"Run #{run_id} | {timestamp} | {attack} ({experiment})"

        with st.expander(title):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Agents",       f"{num_agents}")
            c2.metric("Final Compromised",   f"{total_comp}")
            c3.metric("Impact Rate",
                      f"{(total_comp / num_agents * 100):.1f}%" if num_agents > 0 else "0%")
            c4.metric("MFA", "Enabled" if mfa else "Disabled")

            st.caption(f"Training: {round(training*100)}% | Segmentation: {round(seg*100)}%")
            st.divider()

            sub1, sub2, sub3 = st.tabs(["📊 Timeline", "🌐 Network Topology", "⚙️ JSON Config"])

            with sub1:
                steps_data = get_history_steps(run_id)
                if steps_data:
                    df = pd.DataFrame(steps_data).set_index("tick")
                    st.markdown("#### Daily infection timeline")
                    st.line_chart(df[["opened", "clicked", "infected"]])
                    if "total_compromised" in df.columns:
                        st.markdown("#### Cumulative compromised")
                        st.area_chart(df["total_compromised"])
                else:
                    st.warning("No step metrics recorded for this run.")

            with sub2:
                st.markdown("#### Topology Snapshot")
                if graph_data:
                    total_edges = sum(len(v) for v in graph_data.values())
                    g1, g2 = st.columns(2)
                    g1.metric("Agents in network", f"{len(graph_data)}")
                    g2.metric("Trust connections", f"{total_edges}")
                    st.markdown("##### Sample (first 5 agents)")
                    for agent in list(graph_data.keys())[:5]:
                        links = graph_data[agent]
                        targets = [f"Agent {l['target']} (w: {l['weight']:.2f})" for l in links]
                        st.text(f"Agent {agent} → {', '.join(targets) if targets else 'no connections'}")
                    if len(graph_data) > 5:
                        st.caption(f"... and {len(graph_data)-5} more agents in the database.")
                else:
                    st.warning("No topology recorded for this run.")

            with sub3:
                st.markdown("#### Saved parameters")
                st.json(config_data)


if __name__ == "__main__":
    show()