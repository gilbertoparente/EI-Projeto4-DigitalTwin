import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.api_client import get_graph


EXPERIMENT_TABS = ["No training", "50% training", "MFA"]


def show():
    st.title("Network Topology")
    st.markdown("Explore the network with zoom, pan, and agent selection.")

    graph_data = get_graph()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.warning("Initialize the Digital Twin in Experiments first.")
        return

    if "exp1_history" not in st.session_state or not st.session_state.exp1_history:
        st.info("Run experiments in Analytics before opening network comparison.")
        return

    g_tab1, g_tab2, g_tab3 = st.tabs(EXPERIMENT_TABS)

    st.divider()
    total_days = len(st.session_state.exp1_history)
    selected_day = st.slider("Simulation Day", 1, total_days, total_days)
    day_index = selected_day - 1

    with g_tab1:
        _render_experiment_graph(
            nodes,
            edges,
            st.session_state.exp1_history[day_index]["total_network_infection"],
            "No training",
            "Attack configured without training and without MFA.",
            "network_no_training",
        )

    with g_tab2:
        _render_experiment_graph(
            nodes,
            edges,
            st.session_state.exp2_history[day_index]["total_network_infection"],
            "50% training",
            "Attack configured with half the agents trained.",
            "network_half_training",
        )

    with g_tab3:
        _render_experiment_graph(
            nodes,
            edges,
            st.session_state.exp3_history[day_index]["total_network_infection"],
            "MFA",
            "Attack configured with MFA enabled.",
            "network_mfa",
        )


def _render_experiment_graph(nodes, edges, infected_count, title, caption, state_key):
    st.subheader(title)
    st.caption(caption)

    calculated_infected = min(infected_count, len(nodes))
    st.metric("Compromised Agents", f"{calculated_infected} / {len(nodes)}")

    graph_nodes = _prepare_nodes(nodes, edges, calculated_infected)
    default_node = next((node for node in graph_nodes if node["infected"]), graph_nodes[0] if graph_nodes else None)
    selected_id = st.session_state.get(state_key, default_node["id"] if default_node else None)

    fig = _build_plotly_graph(graph_nodes, edges, selected_id)
    event = st.plotly_chart(
        fig,
        key=f"{state_key}_plot",
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )

    clicked_id = _selected_node_id(event)
    if clicked_id is not None and clicked_id != selected_id:
        st.session_state[state_key] = clicked_id
        st.rerun()

    _render_selected_agent_panel(graph_nodes, edges, selected_id)
    render_snapshot_breakdown(nodes, calculated_infected)


def _prepare_nodes(nodes, edges, infected_count):
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node["id"])
    for edge in edges:
        graph.add_edge(edge["source"], edge["target"], weight=edge.get("weight", 0.5))

    positions = nx.spring_layout(graph, seed=42, k=0.55) if graph.number_of_nodes() else {}

    prepared = []
    for idx, node in enumerate(nodes):
        x, y = positions.get(node["id"], [0.0, 0.0])
        prepared.append(
            {
                "id": node["id"],
                "label": node.get("label", str(node["id"])),
                "department": node.get("department", "General"),
                "hierarchy": node.get("hierarchy_level", node.get("hierarchy", 1)),
                "awareness": node.get("awareness", 0),
                "risk": node.get("risk", 0),
                "infected": idx < infected_count,
                "x": x,
                "y": y,
            }
        )
    return prepared


def _build_plotly_graph(nodes, edges, selected_id):
    node_by_id = {node["id"]: node for node in nodes}
    inactive_x, inactive_y = [], []
    active_x, active_y = [], []

    for edge in edges:
        source = node_by_id.get(edge["source"])
        target = node_by_id.get(edge["target"])
        if not source or not target:
            continue

        x_values = [source["x"], target["x"], None]
        y_values = [source["y"], target["y"], None]
        if edge["source"] == selected_id or edge["target"] == selected_id:
            active_x.extend(x_values)
            active_y.extend(y_values)
        else:
            inactive_x.extend(x_values)
            inactive_y.extend(y_values)

    edge_trace = go.Scatter(
        x=inactive_x,
        y=inactive_y,
        mode="lines",
        line={"width": 1, "color": "#CBD5E1"},
        hoverinfo="skip",
        showlegend=False,
    )
    active_edge_trace = go.Scatter(
        x=active_x,
        y=active_y,
        mode="lines",
        line={"width": 3, "color": "#2563EB"},
        hoverinfo="skip",
        showlegend=False,
    )

    node_trace = go.Scatter(
        x=[node["x"] for node in nodes],
        y=[node["y"] for node in nodes],
        mode="markers+text",
        text=[node["label"] for node in nodes],
        textposition="top center",
        customdata=[
            [
                node["id"],
                node["department"],
                node["hierarchy"],
                "Infected" if node["infected"] else "Clean",
                node["awareness"],
                node["risk"],
            ]
            for node in nodes
        ],
        marker={
            "size": [24 if node["id"] == selected_id else 15 for node in nodes],
            "color": ["#EF4444" if node["infected"] else "#22C55E" for node in nodes],
            "line": {
                "width": [4 if node["id"] == selected_id else 1.5 for node in nodes],
                "color": ["#111827" if node["id"] == selected_id else "#FFFFFF" for node in nodes],
            },
        },
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Status: %{customdata[3]}<br>"
            "Dept: %{customdata[1]}<br>"
            "Level: %{customdata[2]}<br>"
            "Awareness: %{customdata[4]}<br>"
            "Risk: %{customdata[5]}"
            "<extra></extra>"
        ),
        showlegend=False,
    )

    fig = go.Figure(data=[edge_trace, active_edge_trace, node_trace])
    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#FFFFFF",
        dragmode="pan",
        hovermode="closest",
        xaxis={"showgrid": False, "zeroline": False, "visible": False},
        yaxis={"showgrid": False, "zeroline": False, "visible": False},
    )
    return fig


def _selected_node_id(event):
    try:
        points = event.selection.points
    except AttributeError:
        return None

    if not points:
        return None

    customdata = points[0].get("customdata")
    if not customdata:
        return None
    return customdata[0]


def _render_selected_agent_panel(nodes, edges, selected_id):
    node_by_id = {node["id"]: node for node in nodes}
    selected = node_by_id.get(selected_id)

    if not selected:
        st.info("Select an agent on the graph.")
        return

    connected_edges = [
        edge for edge in edges if edge["source"] == selected_id or edge["target"] == selected_id
    ]

    st.markdown("#### Selected Agent")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Name", selected["label"])
    c2.metric("Status", "Infected" if selected["infected"] else "Clean")
    c3.metric("Dept", selected["department"])
    c4.metric("Connections", len(connected_edges))

    rows = []
    for edge in connected_edges:
        other_id = edge["target"] if edge["source"] == selected_id else edge["source"]
        other_node = node_by_id.get(other_id)
        if other_node:
            rows.append(
                {
                    "Connected Agent": other_node["label"],
                    "Status": "Infected" if other_node["infected"] else "Clean",
                    "Department": other_node["department"],
                    "Weight": round(edge.get("weight", 0.5), 2),
                }
            )

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("This agent has no registered connections.")


def render_snapshot_breakdown(nodes, target_infected_count):
    st.markdown("#### Breakdown by Department and Hierarchy")

    stats = {}
    for idx, node in enumerate(nodes):
        if idx >= target_infected_count:
            continue

        dept = node.get("department", "General")
        level = node.get("hierarchy_level", 1)

        if dept not in stats:
            stats[dept] = {"Level 1": 0, "Level 2": 0, "Level 3": 0}

        stats[dept][f"Level {level}"] = stats[dept].get(f"Level {level}", 0) + 1

    if stats:
        st.dataframe(pd.DataFrame.from_dict(stats, orient="index").fillna(0).astype(int), use_container_width=True)
    else:
        st.success("No infected agents in this snapshot.")


if __name__ == "__main__":
    show()