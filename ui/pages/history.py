import pandas as pd
import requests
import streamlit as st


def show():
    st.title("📜 Simulation History")
    st.markdown("Consult and compare past simulation runs stored in the Digital Twin database.")

    try:
        response = requests.get("http://127.0.0.1:8000/history")
        if response.status_code != 200:
            st.error("Failed to fetch history from the API.")
            return

        runs = response.json().get("runs", [])
    except Exception:
        st.error("Could not connect to the API server. Ensure backend is running.")
        return

    if not runs:
        st.info("No simulations found in the history database yet. Run some experiments first!")
        return

    for run in runs:
        run_id = run["id"]
        timestamp = run["timestamp"]
        experiment = run["experiment_type"]
        attack = run["attack_type"]
        total_compromised = run["total_compromised"]
        num_agents = run["num_agents"]
        config_data = run["config"]
        graph_data = run.get("graph", {})  # NOVO: Puxa o grafo que o servidor enviou

        title = f"Run #{run_id} | {timestamp} | {attack} ({experiment})"

        with st.expander(title):
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Agents", f"{num_agents} nodes")
            c2.metric("Final Compromised", f"{total_compromised} nodes")
            c3.metric("Impact Rate", f"{(total_compromised / num_agents * 100):.1f}%" if num_agents > 0 else "0%")

            st.divider()

            # CORREÇÃO: Adicionado o terceiro separador para a Topologia da Rede
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📊 Evolution Chart", "🌐 Network Topology", "⚙️ JSON Configuration"])

            with sub_tab1:
                try:
                    steps_resp = requests.get(f"http://127.0.0.1:8000/history/steps/{run_id}")
                    if steps_resp.status_code == 200:
                        steps_data = steps_resp.json()
                        if steps_data:
                            df = pd.DataFrame(steps_data).set_index("tick")
                            st.markdown("#### Daily Infection Evolution")
                            st.line_chart(df[["opened", "clicked", "infected"]])
                        else:
                            st.warning("No step metrics recorded for this run.")
                except Exception:
                    st.error("Error loading evolution data for this chart.")

            # NOVO: Renderizar a informação do grafo histórico
            with sub_tab2:
                st.markdown("#### Network Topology Map Snapshot")
                if graph_data:
                    # Calcular o número total de ligações (arestas) no grafo guardado
                    total_edges = sum(len(connections) for connections in graph_data.values())

                    col_g1, col_g2 = st.columns(2)
                    col_g1.metric("Network Nodes", f"{len(graph_data)} agents")
                    col_g2.metric("Total Trust Links", f"{total_edges} edges")

                    st.markdown("##### Node Connections (Sample)")
                    # Mostra as conexões dos primeiros 5 agentes para não sobrecarregar o ecrã
                    sample_agents = list(graph_data.keys())[:5]
                    for agent in sample_agents:
                        links = graph_data[agent]
                        targets = [f"Agent {l['target']} (w: {l['weight']:.2f})" for l in links]
                        st.text(f"Agent {agent} connects to -> {', '.join(targets)}")

                    if len(graph_data) > 5:
                        st.caption(f"... and {len(graph_data) - 5} more agents stored in database.")
                else:
                    st.warning("No graph topology was recorded for this simulation run.")

            with sub_tab3:
                st.markdown("#### Saved Parameters")
                st.json(config_data)