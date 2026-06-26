import copy
import pandas as pd
import requests
import streamlit as st
from ui.api_client import run_analytics

EXPERIMENT_LABELS = {
    "exp1": "No training",
    "exp2": "50% training",
    "exp3": "MFA",
}


def _render_tab(history, title, description):
    st.subheader(title)
    st.caption(description)
    if not history:
        st.info("Run the experiments using the control panel above.")
        return

    df = pd.DataFrame(history).set_index("tick")
    st.markdown("#### Attack Funnel")
    st.line_chart(df[["opened", "clicked", "infected"]])
    st.markdown("#### Cumulative Compromised")
    st.area_chart(df["total_network_infection"])
    st.markdown("#### Logs")
    styled = df.style.background_gradient(cmap="Reds",
               subset=["infected", "total_network_infection"])
    st.dataframe(styled, use_container_width=True)


def show():
    st.title("Analytics & Benchmarking")
    st.markdown("Compare the configured attack against three defensive experiments.")

    if "current_config" not in st.session_state:
        st.warning("Configure and initialize the Digital Twin on the Experiments page first.")
        return

    base_config       = st.session_state["current_config"]
    attack_configured = base_config.get("attack", {}).get("type", "Phishing")

    for key in ["exp1_history", "exp2_history", "exp3_history"]:
        if key not in st.session_state:
            st.session_state[key] = []

    with st.container(border=True):
        st.subheader("Simulation Parameters")
        c1, c2, c3 = st.columns(3)
        selected_attack = c1.radio("Attack type", ["Phishing", "Spear Phishing"],
                                   index=0 if attack_configured == "Phishing" else 1)
        global_intensity = c2.slider("Global intensity", 0.0, 1.0,
                                     float(base_config.get("attack_params", {}).get("global_intensity", 0.5)))
        training_eff = c3.slider("Training effectiveness", 0.0, 1.0,
                                 float(base_config.get("attack_params", {}).get("global_training", 0.3)))
        sim_days = st.number_input("Simulation days", min_value=1, max_value=365, value=15)

        if st.button("🚀 Run Experiments", type="primary", use_container_width=True):
            cfg = copy.deepcopy(base_config)
            cfg["attack_params"]["global_intensity"] = global_intensity
            cfg["attack_params"]["global_training"]  = training_eff

            with st.spinner("Simulating scenarios..."):
                result = run_analytics(cfg, int(sim_days), selected_attack)

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.session_state.exp1_history = result.get("exp1", [])
                st.session_state.exp2_history = result.get("exp2", [])
                st.session_state.exp3_history = result.get("exp3", [])
                st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([
        EXPERIMENT_LABELS["exp1"],
        EXPERIMENT_LABELS["exp2"],
        EXPERIMENT_LABELS["exp3"],
        "Report",
    ])

    with tab1:
        _render_tab(st.session_state.exp1_history, EXPERIMENT_LABELS["exp1"],
                    "Baseline — no training, no MFA.")
    with tab2:
        _render_tab(st.session_state.exp2_history, EXPERIMENT_LABELS["exp2"],
                    "50% training effectiveness active.")
    with tab3:
        _render_tab(st.session_state.exp3_history, EXPERIMENT_LABELS["exp3"],
                    "MFA enabled (90% block rate).")

    with tab4:
        st.subheader("Strategic Matrix")
        if st.session_state.exp1_history:
            histories = [st.session_state.exp1_history,
                         st.session_state.exp2_history,
                         st.session_state.exp3_history]
            labels = list(EXPERIMENT_LABELS.values())
            df_compare = pd.DataFrame({
                label: [d["total_network_infection"] for d in hist]
                for label, hist in zip(labels, histories)
            })
            df_compare.index = range(1, len(df_compare) + 1)

            st.markdown("### Cumulative compromised")
            st.line_chart(df_compare)

            matrix_data = {
                "Metric": ["Attack", "Training", "MFA", "Daily peak", "Final compromised"],
                EXPERIMENT_LABELS["exp1"]: [selected_attack, "0%", "Disabled",
                    str(max(d["infected"] for d in st.session_state.exp1_history)),
                    str(df_compare[EXPERIMENT_LABELS["exp1"]].iloc[-1])],
                EXPERIMENT_LABELS["exp2"]: [selected_attack, "50%", "Disabled",
                    str(max(d["infected"] for d in st.session_state.exp2_history)),
                    str(df_compare[EXPERIMENT_LABELS["exp2"]].iloc[-1])],
                EXPERIMENT_LABELS["exp3"]: [selected_attack, "0%", "Enabled",
                    str(max(d["infected"] for d in st.session_state.exp3_history)),
                    str(df_compare[EXPERIMENT_LABELS["exp3"]].iloc[-1])],
            }
            st.table(pd.DataFrame(matrix_data).set_index("Metric"))

            csv = df_compare.to_csv().encode("utf-8")
            st.download_button("📥 Export CSV", data=csv,
                               file_name="analytics_report.csv", mime="text/csv")
        else:
            st.info("Run the experiments to see the Strategic Matrix.")


if __name__ == "__main__":
    show()