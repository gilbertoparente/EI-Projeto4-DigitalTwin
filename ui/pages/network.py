import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui.api_client import get_graph


def show():
    st.title("🕸️ Network Topology")
    st.markdown("Trust network visualization between agents. Red = compromised | Green = clean.")

    if st.button("Refresh graph"):
        st.rerun()

    graph_data = get_graph()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.warning("Initialize the Digital Twin in Experiments first.")
        return

    total_inf   = sum(1 for n in nodes if n.get("state") == "infected")
    total_clean = len(nodes) - total_inf

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total agents", len(nodes))
    m2.metric("Clean",        total_clean)
    m3.metric("Infected",     total_inf)
    if len(nodes) > 0:
        m4.metric("Infection rate", f"{round(total_inf/len(nodes)*100, 1)}%")

    st.divider()

    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"])
    for e in edges:
        G.add_edge(e["source"], e["target"], weight=e.get("weight", 0.5))

    pos = nx.spring_layout(G, seed=42, k=0.55) if G.number_of_nodes() else {}

    prepared = []
    for n in nodes:
        x, y = pos.get(n["id"], [0.0, 0.0])
        prepared.append({
            "id":         n["id"],
            "label":      n.get("label", str(n["id"])),
            "department": n.get("department", "N/A"),
            "hierarchy":  n.get("hierarchy_level", n.get("hierarchy", 1)),
            "awareness":  n.get("awareness", 0),
            "risk":       n.get("risk", 0),
            "education":  n.get("education", "N/A"),
            "infected":   n.get("state") == "infected",
            "x": x, "y": y,
        })

    selected_id = st.session_state.get("network_selected_id",
                                        next((n["id"] for n in prepared if n["infected"]),
                                             prepared[0]["id"] if prepared else None))

    node_by_id = {n["id"]: n for n in prepared}
    inactive_x, inactive_y = [], []
    active_x,   active_y   = [], []
    for e in edges:
        s = node_by_id.get(e["source"])
        t = node_by_id.get(e["target"])
        if not s or not t:
            continue
        xs = [s["x"], t["x"], None]
        ys = [s["y"], t["y"], None]
        if e["source"] == selected_id or e["target"] == selected_id:
            active_x.extend(xs); active_y.extend(ys)
        else:
            inactive_x.extend(xs); inactive_y.extend(ys)

    edge_trace = go.Scatter(x=inactive_x, y=inactive_y, mode="lines",
                             line={"width": 1, "color": "#30363d"}, hoverinfo="skip", showlegend=False)
    active_edge_trace = go.Scatter(x=active_x, y=active_y, mode="lines",
                                    line={"width": 2.5, "color": "#58a6ff"}, hoverinfo="skip", showlegend=False)

    node_trace = go.Scatter(
        x=[n["x"] for n in prepared],
        y=[n["y"] for n in prepared],
        mode="markers+text",
        text=[n["label"] for n in prepared],
        textposition="top center",
        customdata=[
            [n["id"], n["department"], n["hierarchy"],
             "Infected" if n["infected"] else "Clean",
             n["awareness"], n["risk"], n["education"]]
            for n in prepared
        ],
        marker={
            "size":  [22 if n["id"] == selected_id else 14 for n in prepared],
            "color": ["#f85149" if n["infected"] else "#3fb950" for n in prepared],
            "line":  {
                "width": [4 if n["id"] == selected_id else 1.5 for n in prepared],
                "color": ["#e6edf3" if n["id"] == selected_id else "#0d1117" for n in prepared],
            },
        },
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Status: %{customdata[3]}<br>"
            "Dept: %{customdata[1]}<br>"
            "Level: %{customdata[2]}<br>"
            "Education: %{customdata[6]}<br>"
            "Awareness: %{customdata[4]}<br>"
            "Risk: %{customdata[5]}"
            "<extra></extra>"
        ),
        showlegend=False,
    )

    fig = go.Figure(data=[edge_trace, active_edge_trace, node_trace])
    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        dragmode="pan",
        hovermode="closest",
        xaxis={"showgrid": False, "zeroline": False, "visible": False},
        yaxis={"showgrid": False, "zeroline": False, "visible": False},
        height=520,
    )

    event = st.plotly_chart(
        fig, key="network_plot", use_container_width=True,
        on_select="rerun", selection_mode="points",
        config={"scrollZoom": True, "displaylogo": False},
    )

    try:
        points = event.selection.points
        if points:
            cd = points[0].get("customdata")
            if cd:
                clicked = cd[0]
                if clicked != selected_id:
                    st.session_state["network_selected_id"] = clicked
                    st.rerun()
    except AttributeError:
        pass

    sel = node_by_id.get(selected_id)
    if sel:
        conn_edges = [e for e in edges if e["source"] == selected_id or e["target"] == selected_id]
        st.markdown("#### Selected Agent")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Name",        sel["label"])
        c2.metric("Status",      "Infected" if sel["infected"] else "Clean")
        c3.metric("Dept",        sel["department"])
        c4.metric("Education",   sel["education"])
        c5.metric("Connections", len(conn_edges))

        rows = []
        for e in conn_edges:
            other_id   = e["target"] if e["source"] == selected_id else e["source"]
            other_node = node_by_id.get(other_id)
            if other_node:
                rows.append({
                    "Agent":      other_node["label"],
                    "Status":     "Infected" if other_node["infected"] else "Clean",
                    "Department": other_node["department"],
                    "Education":  other_node["education"],
                    "Weight":     round(e.get("weight", 0.5), 2),
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### Department Breakdown")
    dept_stats: dict = {}
    for n in nodes:
        d = n.get("department", "N/A")
        if d not in dept_stats:
            dept_stats[d] = {"total": 0, "infected": 0}
        dept_stats[d]["total"] += 1
        if n.get("state") == "infected":
            dept_stats[d]["infected"] += 1
    for dept in dept_stats:
        dept_stats[dept]["rate"] = round(
            dept_stats[dept]["infected"] / max(dept_stats[dept]["total"], 1) * 100, 1
        )
    st.dataframe(pd.DataFrame.from_dict(dept_stats, orient="index"), use_container_width=True)


if __name__ == "__main__":
    show()