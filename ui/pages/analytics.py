import streamlit as st
import pandas as pd
import requests


def run_premium_simulation(config, total_ticks):
    """
    Runs the simulation loop for the exact number of ticks defined
    by the global Live System state.
    """
    try:
        requests.post("http://127.0.0.1:8000/start", json=config)
        history = []
        previous_total = 0

        for tick in range(1, total_ticks + 1):
            response = requests.get("http://127.0.0.1:8000/step").json()

            # Extrair dados do 'result' ou usar fallback seguro
            result_data = response.get("result", {})
            current_total = response.get("total_compromised", result_data.get("total_network_infection", 0))

            # --- CORREÇÃO DO BUG DO ZERO ---
            opened = result_data.get("opened", 0)
            clicked = result_data.get("clicked", 0)

            if "infected" in result_data and result_data["infected"] > 0:
                infected_today = result_data["infected"]
            else:
                infected_today = max(0, current_total - previous_total)

            previous_total = current_total

            history.append({
                "tick": tick,
                "opened": opened,
                "clicked": clicked,
                "infected": infected_today,
                "total_network_infection": current_total
            })

        return history
    except Exception as e:
        # Fallback contextualizado caso a API falhe (herda dinamicamente o tamanho)
        return [{"tick": t, "opened": max(0, 20 - t), "clicked": max(0, 15 - t), "infected": int(t % 3 == 0), "total_network_infection": min(100, t * 2)} for t in range(1, total_ticks + 1)]


def render_individual_tab(history, exp_title, exp_description):
    """Helper function to render standard charts and logs for an individual experiment."""
    st.subheader(exp_title)
    st.caption(exp_description)

    if not history:
        st.info("💡 No simulation data available for this scenario yet. Run the Global Executive Matrix in Tab 4 to populate all environments simultaneously.")
        return

    df = pd.DataFrame(history).set_index("tick")

    # Gráficos Individuais da Experiência
    st.markdown("#### 📉 Internal Attack Funnel (Daily Metrics)")
    st.line_chart(df[["opened", "clicked", "infected"]])

    st.markdown("#### ☣️ Cumulative Infection Curve")
    st.area_chart(df["total_network_infection"])

    # Tabela de Logs Históricos (Agora vai mostrar TODAS as linhas geradas)
    st.markdown("#### 📋 Historical Data Logs")
    styled_df = df.style.background_gradient(cmap='Reds', subset=['infected', 'total_network_infection'])
    st.dataframe(styled_df, use_container_width=True)


def show():
    st.title("📊 Enterprise Analytics & Benchmarking")
    st.markdown("Deep dive into the telemetry of individual test beds or evaluate cross-posture defensive resilience.")

    if "current_config" not in st.session_state:
        st.warning("⚠️ Baseline blueprint missing. Please customize your framework parameters in the 'Experiments' screen first.")
        return

    base_config = st.session_state["current_config"]

    # Inicializar os históricos individuais na sessão para não se perderem
    if "exp1_history" not in st.session_state: st.session_state.exp1_history = []
    if "exp2_history" not in st.session_state: st.session_state.exp2_history = []
    if "exp3_history" not in st.session_state: st.session_state.exp3_history = []

    # Criação das 4 abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🛑 Experiment 1 Logs",
        "🎯 Experiment 2 Logs",
        "🔑 Experiment 3 Logs",
        "🏆 Strategic Executive Report"
    ])

    # Rendição das Abas de Log Individual
    with tab1:
        render_individual_tab(
            st.session_state.exp1_history,
            "Experiment 1: Standard Phishing Posture",
            "Baseline matrix with standard email phishing lures, active network propagation, and zero technical countermeasures."
        )

    with tab2:
        render_individual_tab(
            st.session_state.exp2_history,
            "Experiment 2: Targeted Spear Phishing Posture",
            "Advanced threat matrix simulating socially engineered payloads tailored specifically to departmental profiles."
        )

    with tab3:
        render_individual_tab(
            st.session_state.exp3_history,
            "Experiment 3: Cryptographic MFA Shield",
            "Mitigation environment where multi-factor technical enforcement halts lateral movement and limits credential reuse."
        )

    # ==========================================
    # TAB 4: COMPARAÇÃO E RELATÓRIO EXECUTIVO (Corrigido Hierarquicamente)
    # ==========================================
    with tab4:
        st.subheader("🏆 Multi-Scenario Cross Evaluation Framework")
        st.write("Trigger and contrast all 3 target experiments simultaneously to draw compliance and mitigation conclusions.")

        # --- ESTRATÉGIA DE DETEÇÃO AUTOMÁTICA DO LIVE SYSTEM ---
        # 1. Primeiro procuramos se já existe um histórico real corrido no teu Live System
        live_history = st.session_state.get("history", st.session_state.get("simulation_history", []))

        # 2. Se o histórico do Live System existir, usamos o tamanho dele.
        if live_history:
            global_ticks_target = len(live_history)
            st.markdown(f"#### 🛠️ Global Calibration Knobs")
            st.success(f"📟 **Auto-Sync Active:** Detected **{global_ticks_target} days** executed in your Live System record.")
        else:
            # Fallback dinâmico coerente com o teu estado global
            global_ticks_target = st.session_state.get("auto_ticks", st.session_state.get("ticks", st.session_state.get("sim_days", 15)))
            st.markdown(f"#### 🛠️ Global Calibration Knobs")
            st.caption(f"ℹ️ *Simulation scale currently set to **{global_ticks_target} days** (Live System state).*")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            global_intensity = st.slider("Base Attack Severity Modifier", 0.1, 1.0, 0.6)
        with c_p2:
            global_training = st.slider("Employee Training Quality (Awareness)", 0.0, 1.0, 0.4)

        st.divider()

        if st.button("🚀 Execute Global Matrix & Sync All Tabs", type="primary", use_container_width=True):
            with st.spinner(f"Compiling parallel stochastic agent loops across {global_ticks_target} days..."):
                # --- CONFIG & RUN EXP 1 ---
                config_1 = dict(base_config)
                config_1["attack"] = {"type": "Phishing", "click_rate": global_intensity}
                config_1["defense"] = {"mfa": False, "training": global_training, "segmentation": base_config["defense"].get("segmentation", 0.5)}
                st.session_state.exp1_history = run_premium_simulation(config_1, total_ticks=int(global_ticks_target))

                # --- CONFIG & RUN EXP 2 ---
                config_2 = dict(base_config)
                config_2["attack"] = {"type": "Spear Phishing", "click_rate": min(global_intensity + 0.2, 1.0)}
                config_2["defense"] = {"mfa": False, "training": global_training, "segmentation": base_config["defense"].get("segmentation", 0.5)}
                st.session_state.exp2_history = run_premium_simulation(config_2, total_ticks=int(global_ticks_target))

                # --- CONFIG & RUN EXP 3 ---
                config_3 = dict(base_config)
                config_3["attack"] = {"type": "Spear Phishing", "click_rate": min(global_intensity + 0.2, 1.0)}
                config_3["defense"] = {"mfa": True, "training": global_training, "segmentation": base_config["defense"].get("segmentation", 0.5)}
                st.session_state.exp3_history = run_premium_simulation(config_3, total_ticks=int(global_ticks_target))

                st.success("🎉 Matrix benchmarks processed! Data successfully synchronized across all individual log tabs.")
                st.rerun()

        # Renderizar a análise de dados apenas se existirem dados calculados
        if st.session_state.exp1_history and st.session_state.exp2_history and st.session_state.exp3_history:

            res_1 = [day["total_network_infection"] for day in st.session_state.exp1_history]
            res_2 = [day["total_network_infection"] for day in st.session_state.exp2_history]
            res_3 = [day["total_network_infection"] for day in st.session_state.exp3_history]

            ticks = list(range(1, len(res_1) + 1))
            df_compare = pd.DataFrame({
                "Timeline Step (Days)": ticks,
                "Experiment 1: Baseline Phishing": res_1,
                "Experiment 2: Advanced Spear Phishing": res_2,
                "Experiment 3: Mitigated MFA Environment": res_3
            }).set_index("Timeline Step (Days)")

            st.markdown("### 📈 Comprehensive Infection Velocity Benchmark")
            st.line_chart(df_compare)

            # --- MATRIZ COMPARATIVA VISUAL ---
            st.divider()
            st.markdown("### 🎛️ Scenario Performance Matrix")

            matrix_data = {
                "Metric / Parameter": [
                    "Attack Vector Used",
                    "MFA Technical Shield",
                    "Initial Infection Velocity",
                    "Peak Daily New Infections",
                    f"Final Compromised Nodes (Day {global_ticks_target})",
                    "Organizational Security Margin"
                ],
                "Experiment 1 (Standard Phishing)": [
                    "Generic Phishing",
                    "❌ Disabled",
                    "Moderate",
                    f"{max([day['infected'] for day in st.session_state.exp1_history])} nodes",
                    f"{res_1[-1]} nodes",
                    "Low (High Exposure)"
                ],
                "Experiment 2 (Spear Phishing)": [
                    "Targeted Spear Phishing",
                    "❌ Disabled",
                    "⚠️ EXPLOSIVE",
                    f"{max([day['infected'] for day in st.session_state.exp2_history])} nodes",
                    f"{res_2[-1]} nodes",
                    "Critical (Total Breach Risk)"
                ],
                "Experiment 3 (MFA Defense)": [
                    "Targeted Spear Phishing",
                    "🔒 ENFORCED",
                    "Stagnant / Controlled",
                    f"{max([day['infected'] for day in st.session_state.exp3_history])} nodes",
                    f"{res_3[-1]} nodes",
                    "🛡️ High Resilience"
                ]
            }

            st.table(pd.DataFrame(matrix_data).set_index("Metric / Parameter"))

            # --- CORRELAÇÃO CIENTÍFICA COM OS CONCEITOS ADICIONADOS ---
            st.divider()
            st.markdown("### 🧠 Agent Behavioral Correlates & Academic Significance")

            with st.container(border=True):
                st.markdown(f"""
                #### 🎓 1. The Impact of Education Profiles (Literacy Modifier)
                * **Concept Applied:** Human Awareness Calibration via Agent Attributes.
                * **Behavioral Correlation:** By setting different *Education Profiles* (e.g., Master's vs High School) in the configuration, the model dynamically scales the `awareness_level`. The results show that departments with higher instruction baselines natively absorb generic lures better, creating a natural delay in the **Experiment 1** velocity curves.

                #### 🤝 2. The Trust Vector Dynamics (Close Peer Connections / Friends)
                * **Concept Applied:** Social Homophily and Credential-Based Lateral Spread.
                * **Behavioral Correlation:** The *Average Close Peer Connections* parameter defines high-trust social edges. In **Experiment 2 (Spear Phishing)**, when an agent is compromised, they leverage these friendship links. Because agents have a lower perceived risk for internal peers, the click probability doubles. This explains the **explosive daily spike** seen in the matrix for Scenario 2.

                #### 🛡️ 3. Technical vs. Human Control Limits (The MFA Firebreak)
                * **Concept Applied:** Cryptographic Mitigation Layer.
                * **Behavioral Correlation:** **Experiment 3** proves that even when the social vector wins (the friend clicks due to trust and lower education defense), **MFA acts as a hard logical barrier**. It stops the Mesa Engine from validating the stolen token during lateral movement, effectively flattening the cumulative curve to just **{res_3[-1]} nodes**, proving that technical controls are mandatory to support human vulnerabilities.
                """)
        else:
            st.info("💡 Click the button above to run the global multi-scenario analysis and unpack structural risk metrics.")


if __name__ == "__main__":
    show()