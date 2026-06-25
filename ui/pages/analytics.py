import copy
import pandas as pd
import requests
import streamlit as st

EXPERIMENT_LABELS = {
    "no_training": "No training",
    "half_training": "50% training coverage",
    "mfa": "MFA",
}


def run_premium_simulation(config, total_ticks):
    try:
        requests.post("http://127.0.0.1:8000/start", json=config)
        history = []
        previous_total = 0

        for tick in range(1, total_ticks + 1):
            response = requests.get("http://127.0.0.1:8000/step").json()
            result_data = response.get("result", {})
            current_total = response.get("total_compromised", result_data.get("total_network_infection", 0))

            opened = result_data.get("opened", 0)
            clicked = result_data.get("clicked", 0)
            infected_today = result_data.get("infected", max(0, current_total - previous_total))
            previous_total = current_total

            history.append(
                {
                    "tick": tick,
                    "opened": opened,
                    "clicked": clicked,
                    "infected": infected_today,
                    "total_network_infection": current_total,
                }
            )

        return history
    except Exception:
        return []


def render_individual_tab(history, title, description):
    st.subheader(title)
    st.caption(description)

    if not history:
        st.info("Run the experiments using the control panel above.")
        return

    df = pd.DataFrame(history).set_index("tick")
    st.markdown("#### Attack Funnel")
    st.line_chart(df[["opened", "clicked", "infected"]])

    st.markdown("#### Cumulative Compromise")
    st.area_chart(df["total_network_infection"])

    st.markdown("#### Logs")
    styled_df = df.style.background_gradient(cmap="Reds", subset=["infected", "total_network_infection"])
    st.dataframe(styled_df, use_container_width=True)


def show():
    st.title("Analytics & Benchmarking")
    st.markdown("Compare the configured attack against three defensive experiments.")

    if "current_config" not in st.session_state:
        st.warning("Configure and initialize the Digital Twin on the Experiments page first.")
        return

    base_config = st.session_state["current_config"]
    attack_configured = base_config.get("attack", {}).get("type", "Phishing")

    # Inicialização de estado
    for key in ["exp1_history", "exp2_history", "exp3_history"]:
        if key not in st.session_state: st.session_state[key] = []

    # --- 🌍 CONTROLOS GLOBAIS (NO TOPO) ---
    with st.container(border=True):
        st.subheader("Global Simulation Parameters")
        c1, c2, c3 = st.columns(3)
        selected_attack = c1.radio("Configured attack", ["Phishing", "Spear Phishing"],
                                   index=0 if attack_configured == "Phishing" else 1)
        global_intensity = c2.slider("Global Intensity", 0.0, 1.0,
                                     float(base_config.get("attack_params", {}).get("global_intensity", 0.5)))
        training_eff = c3.slider("Training Effectiveness", 0.0, 1.0,
                                 float(base_config.get("attack_params", {}).get("global_training", 0.3)))

        sim_days = st.number_input("Simulation days", min_value=1, max_value=365, value=15)

        if st.button("🚀 Run Experiments", type="primary", use_container_width=True):
            with st.spinner("Simulating scenarios..."):
                # Passamos o nome exato como o último argumento de cada cenário
                st.session_state.exp1_history = run_premium_simulation(
                    _scenario_config(base_config, selected_attack, global_intensity, training_eff, 0.0, False,
                                     "No training"), int(sim_days))
                st.session_state.exp2_history = run_premium_simulation(
                    _scenario_config(base_config, selected_attack, global_intensity, training_eff, 0.5, False,
                                     "50% training coverage"), int(sim_days))
                st.session_state.exp3_history = run_premium_simulation(
                    _scenario_config(base_config, selected_attack, global_intensity, training_eff, 0.0, True, "MFA"),
                    int(sim_days))
            st.rerun()

    # --- 📊 TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(
        [EXPERIMENT_LABELS["no_training"], EXPERIMENT_LABELS["half_training"], EXPERIMENT_LABELS["mfa"], "Report"])

    with tab1:
        render_individual_tab(st.session_state.exp1_history, EXPERIMENT_LABELS["no_training"], "Base configuration.")
    with tab2:
        render_individual_tab(st.session_state.exp2_history, EXPERIMENT_LABELS["half_training"], "50% training.")
    with tab3:
        render_individual_tab(st.session_state.exp3_history, EXPERIMENT_LABELS["mfa"], "MFA enabled.")

    with tab4:
        st.subheader("Strategic Matrix & Report")
        if st.session_state.exp1_history:
            histories = [st.session_state.exp1_history, st.session_state.exp2_history, st.session_state.exp3_history]
            labels = [EXPERIMENT_LABELS["no_training"], EXPERIMENT_LABELS["half_training"], EXPERIMENT_LABELS["mfa"]]
            df_compare = pd.DataFrame({label: [day["total_network_infection"] for day in history] for label, history in
                                       zip(labels, histories)})
            df_compare.index = range(1, len(df_compare) + 1)

            st.markdown("### Cumulative compromise comparison")
            st.line_chart(df_compare)

            matrix_data = {
                "Metric": ["Attack used", "Training coverage", "MFA", "Daily peak", "Final compromised nodes"],
                EXPERIMENT_LABELS["no_training"]: [selected_attack, "0%", "Inactive",
                                                   f"{max(d['infected'] for d in st.session_state.exp1_history)}",
                                                   f"{df_compare[EXPERIMENT_LABELS['no_training']].iloc[-1]}"],
                EXPERIMENT_LABELS["half_training"]: [selected_attack, "50%", "Inactive",
                                                     f"{max(d['infected'] for d in st.session_state.exp2_history)}",
                                                     f"{df_compare[EXPERIMENT_LABELS['half_training']].iloc[-1]}"],
                EXPERIMENT_LABELS["mfa"]: [selected_attack, "0%", "Active",
                                           f"{max(d['infected'] for d in st.session_state.exp3_history)}",
                                           f"{df_compare[EXPERIMENT_LABELS['mfa']].iloc[-1]}"],
            }
            st.table(pd.DataFrame(matrix_data).set_index("Metric"))
        else:
            st.info("Run the experiments to see the Strategic Matrix.")


def _scenario_config(base_config, attack_type, intensity, training_effectiveness, training_coverage, mfa, label):
    import copy
    config = copy.deepcopy(base_config)

    # Injeta a etiqueta correta para a Base de Dados ler sem margem para erros
    config["experiment_label"] = label

    config["attack"] = {"type": attack_type}
    config.setdefault("attack_params", {})
    config["attack_params"]["global_intensity"] = intensity
    config["attack_params"]["global_training"] = training_effectiveness
    config.setdefault("defense", {})
    config["defense"]["mfa"] = mfa
    config["defense"]["training"] = training_effectiveness
    config["defense"]["training_coverage"] = training_coverage
    return config


if __name__ == "__main__":
    show()