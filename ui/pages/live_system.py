import streamlit as st
import time
import pandas as pd
from ui.api_client import step_simulation, get_status

_TABLER_CDN = (
    "<link rel='stylesheet' "
    "href='https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css'>"
)


def _metric_with_tip(col, label, value, tip, delta=None):
    with col:
        st.metric(label, value, delta=delta, help=tip)


def _section_heading(label: str, color: str = "#58a6ff"):
    st.markdown(
        f"""<div style="border-left:3px solid {color}; padding-left:12px; margin-bottom:.75rem;">
              <span style="font-size:11px; font-weight:600; color:{color};
                           text-transform:uppercase; letter-spacing:.06em;">{label}</span>
            </div>""",
        unsafe_allow_html=True,
    )


def _alert(msg: str, kind: str = "info"):
    styles = {
        "success": ("#0d2b1d", "#1a6e2d", "#3fb950", "ti-check"),
        "error":   ("#3d0f0f", "#7a2020", "#f85149", "ti-x"),
        "warning": ("#2a1700", "#5a3500", "#e3b341", "ti-alert-triangle"),
        "info":    ("#1a2a4a", "#2d5096", "#58a6ff", "ti-info-circle"),
    }
    bg, border, color, icon = styles.get(kind, styles["info"])
    st.markdown(
        f"""{_TABLER_CDN}
            <div style="display:flex;align-items:center;gap:10px;background:{bg};
                        border:1px solid {border};border-radius:8px;padding:10px 14px;margin:.5rem 0;">
              <i class="ti {icon}" style="color:{color};font-size:16px;flex-shrink:0"></i>
              <span style="color:{color};font-size:13px;">{msg}</span>
            </div>""",
        unsafe_allow_html=True,
    )


def _ensure_history():
    status = get_status()
    run_id = status.get("run_id", None)
    if "ls_run_id" not in st.session_state:
        st.session_state.ls_run_id = run_id
        st.session_state.ls_history = []
    elif st.session_state.ls_run_id != run_id:
        st.session_state.ls_run_id = run_id
        st.session_state.ls_history = []
    if "ls_history" not in st.session_state:
        st.session_state.ls_history = []


def _run_steps(n: int, delay: float = 0.0, stop_on_full: bool = False, total_agents: int = 0):
    _ensure_history()
    progress = st.progress(0, text=f"Running 0 / {n} steps…")
    for i in range(n):
        data = step_simulation()
        if "error" in data:
            _alert(f"Error on step {i+1}: {data['error']}", "error")
            break
        if "result" not in data:
            _alert("Simulation not started. Go to Experiments.", "warning")
            break
        entry = data.get("result", {})
        entry["tick"]  = data.get("tick", len(st.session_state.ls_history) + 1)
        entry["total"] = data.get("total_compromised", 0)
        entry["total_agents"] = data.get("total_agents", 1)
        st.session_state.ls_history.append(entry)
        progress.progress((i + 1) / n, text=f"Running {i+1} / {n} steps…")
        if stop_on_full and total_agents > 0 and entry["total"] >= total_agents:
            break
        if delay > 0 and i < n - 1:
            time.sleep(delay)
    progress.empty()


def _run_until_done(total_agents: int, max_ticks: int = 1000):
    _ensure_history()
    progress = st.progress(0, text="Running until completion…")
    tick_count = 0
    while tick_count < max_ticks:
        data = step_simulation()
        if "error" in data or "result" not in data:
            break
        entry = data.get("result", {})
        entry["tick"]  = data.get("tick", tick_count + 1)
        entry["total"] = data.get("total_compromised", 0)
        entry["total_agents"] = data.get("total_agents", 1)
        st.session_state.ls_history.append(entry)
        tick_count += 1
        pct = min(entry["total"] / max(total_agents, 1), tick_count / max_ticks)
        progress.progress(pct, text=f"Tick {tick_count} — {entry['total']}/{total_agents} compromised…")
        if total_agents > 0 and entry["total"] >= total_agents:
            break
    progress.empty()


def _render_config_summary(config: dict):
    if not config:
        return
    depts   = config.get("organization", {}).get("departments", [])
    attack  = config.get("attack", {})
    defense = config.get("defense", {})

    _section_heading("Active Configuration", "#a371f7")

    if depts:
        dept_cols = st.columns(min(len(depts), 4))
        for i, dept in enumerate(depts[:4]):
            agents = dept.get("agents", [])
            sample = agents[0] if agents else {}
            with dept_cols[i]:
                risk_raw = sample.get("risk_propensity", 0.5)
                aw_raw   = sample.get("awareness_level", 0.5)
                risk_color  = "#f85149" if risk_raw > 0.6 else "#e3b341" if risk_raw > 0.3 else "#3fb950"
                aware_color = "#3fb950" if aw_raw > 0.6 else "#e3b341" if aw_raw > 0.3 else "#f85149"
                st.markdown(
                    f"""<div style="background:#161b22;border:1px solid #21262d;
                                   border-radius:8px;padding:.75rem 1rem;margin-bottom:.5rem;">
                          <div style="font-size:10px;color:#8b949e;text-transform:uppercase;
                                      letter-spacing:.05em;margin-bottom:6px;">{dept['name']}</div>
                          <div style="font-size:12px;color:#e6edf3;margin-bottom:2px;">
                            👥 {len(agents)} agents
                          </div>
                          <div style="font-size:11px;color:{risk_color};">risk {int(risk_raw*100)}%</div>
                          <div style="font-size:11px;color:{aware_color};">aware {int(aw_raw*100)}%</div>
                          <div style="font-size:11px;color:#8b949e;">
                            {sample.get('education_level','—')}
                          </div>
                        </div>""",
                    unsafe_allow_html=True,
                )

    atk_col, def_col = st.columns(2)
    with atk_col:
        atk_type   = attack.get("type", "—")
        click_rate = attack.get("click_rate", 0)
        atk_color  = "#f85149" if atk_type == "Spear Phishing" else "#e3b341"
        st.markdown(
            f"""<div style="background:#161b22;border:1px solid #21262d;
                           border-radius:8px;padding:.75rem 1rem;">
                  <div style="font-size:10px;color:#f78166;text-transform:uppercase;
                              letter-spacing:.05em;margin-bottom:6px;">Attack</div>
                  <div style="font-size:13px;color:{atk_color};font-weight:600;">{atk_type}</div>
                  <div style="font-size:12px;color:#8b949e;margin-top:3px;">
                    Intensity: {int(click_rate*100)}%
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )
    with def_col:
        mfa          = defense.get("mfa", False)
        training     = defense.get("training", 0)
        segmentation = defense.get("segmentation", 0)
        mfa_color    = "#3fb950" if mfa else "#e3b341"
        st.markdown(
            f"""<div style="background:#161b22;border:1px solid #21262d;
                           border-radius:8px;padding:.75rem 1rem;">
                  <div style="font-size:10px;color:#3fb950;text-transform:uppercase;
                              letter-spacing:.05em;margin-bottom:6px;">Defenses</div>
                  <div style="font-size:12px;color:{mfa_color};font-weight:600;">
                    {'🔒 MFA Enabled' if mfa else '⚠️ MFA Disabled'}
                  </div>
                  <div style="font-size:11px;color:#8b949e;margin-top:3px;">
                    Training: {int(training*100)}% · Segmentation: {int(segmentation*100)}%
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )


def show():
    _ensure_history()

    st.markdown("""
    <h1 style='margin-bottom:.25rem'>Live System</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Run the simulation step by step or in batch and track propagation in real time.
    </p>
    """, unsafe_allow_html=True)

    status = get_status()
    offline = "error" in status or status.get("status") == "idle"

    if offline:
        _alert("Simulation not started — go to <strong>Experiments</strong> and click Initialize.", "warning")
        return

    total_agents = status.get("agents", 1)
    current_tick = status.get("tick", 0)
    compromised  = status.get("compromised", 0)
    comp_pct     = round(compromised / max(total_agents, 1) * 100, 1)

    m1, m2, m3, m4 = st.columns(4)
    _metric_with_tip(m1, "Total agents",       total_agents,
                     "Number of CollaboratorAgents created in the organization.")
    _metric_with_tip(m2, "Current tick",       current_tick,
                     "Number of simulation cycles executed.")
    _metric_with_tip(m3, "Compromised",        compromised,
                     "Agents whose credentials have been captured.")
    _metric_with_tip(m4, "Compromise rate",    f"{comp_pct}%",
                     "Percentage of the population compromised.")

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    tab_exec, tab_results = st.tabs(["Execution", "Results"])

    with tab_exec:
        config = st.session_state.get("current_config", {})
        if config:
            _render_config_summary(config)
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                    padding:1.25rem 1.5rem; margin-bottom:1rem;">
        """, unsafe_allow_html=True)

        _section_heading("Execution", "#58a6ff")

        ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 1])
        with ctrl1:
            n_steps = st.selectbox(
                "Steps to run",
                options=[50, 100, 250],
                index=0,
                key="n_steps_select",
            )
        with ctrl2:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            if st.button(f"▶ Run {n_steps} steps", use_container_width=True, type="primary"):
                _run_steps(int(n_steps), delay=0.0)
                st.rerun()
        with ctrl3:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            if st.button("⏩ Run until done", use_container_width=True,
                         help="Runs until all agents are compromised or 1000 ticks pass."):
                _run_until_done(total_agents, max_ticks=1000)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        col_clear, _ = st.columns([1, 4])
        with col_clear:
            if st.button("Clear history"):
                st.session_state.ls_history = []
                st.rerun()

        if not st.session_state.ls_history:
            _alert("Run at least one step to see the charts.", "info")
        else:
            df = pd.DataFrame(st.session_state.ls_history)
            if "tick" in df.columns:
                df = df.set_index("tick")

            st.markdown("""
            <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                        padding:1.25rem 1.5rem; margin-bottom:1rem;">
            """, unsafe_allow_html=True)
            _section_heading("Analytics", "#8b949e")
            chart_cols = st.columns(2)
            with chart_cols[0]:
                st.markdown("<p style='font-size:13px;color:#8b949e;margin-bottom:4px'>Attack funnel per tick</p>",
                            unsafe_allow_html=True)
                funnel_cols = [c for c in ["opened", "clicked", "infected"] if c in df.columns]
                if funnel_cols:
                    st.line_chart(df[funnel_cols], height=220)
            with chart_cols[1]:
                st.markdown("<p style='font-size:13px;color:#8b949e;margin-bottom:4px'>Cumulative compromised</p>",
                            unsafe_allow_html=True)
                if "total" in df.columns:
                    st.area_chart(df["total"], height=220)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_results:
        if not st.session_state.ls_history:
            _alert("Run steps in the <strong>Execution</strong> tab to see results.", "info")
            return

        df = pd.DataFrame(st.session_state.ls_history)

        config  = st.session_state.get("current_config", {})
        attack  = config.get("attack", {})
        defense = config.get("defense", {})
        depts   = config.get("organization", {}).get("departments", [])
        n_agents = sum(len(d.get("agents", [])) for d in depts)

        ticks_run  = len(df)
        final_comp = int(df["total"].iloc[-1]) if "total" in df.columns else 0

        mttd_val = df["mttd"].dropna() if "mttd" in df.columns else pd.Series([], dtype=float)
        mttd     = int(mttd_val.iloc[0]) if not mttd_val.empty else None

        all_comp_tick = None
        if "total" in df.columns and "tick" in df.columns and n_agents > 0:
            reached = df[df["total"] >= n_agents]
            if not reached.empty:
                all_comp_tick = int(reached["tick"].iloc[0])

        infection_rate = round(final_comp / max(n_agents, 1), 4)

        if mttd is not None and final_comp > 0:
            ticks_spreading = (all_comp_tick or ticks_run) - mttd
            spread_rate = round(final_comp / max(ticks_spreading, 1), 4)
        else:
            spread_rate = None

        kpis = [
            ("Infection Rate",              infection_rate,               True,  "KPI"),
            ("Final compromised",           final_comp,                   False, "KPI"),
            ("Total agents",                n_agents,                     False, "KPI"),
            ("MTTD (ticks)",                mttd,                         False, "KPI"),
            ("Tick — all compromised",      all_comp_tick,                False, "KPI"),
            ("Spread rate (comp/tick)",     spread_rate,                  False, "KPI"),
            ("Attack Type",                 attack.get("type", "—"),      False, "CFG"),
            ("MFA",                         defense.get("mfa"),           False, "CFG"),
            ("Training",                    defense.get("training", 0),   True,  "CFG"),
            ("Network Segmentation",        defense.get("segmentation", 0), True, "CFG"),
            ("Ticks run",                   ticks_run,                    False, "CFG"),
        ]

        def _fmt(v, is_pct):
            if v is None:           return "—"
            if isinstance(v, bool): return "Enabled ✅" if v else "Disabled ⚠️"
            if is_pct:              return f"{v * 100:.1f}%"
            if isinstance(v, float): return f"{v:.4f}"
            return str(v)

        def _risk_color(v, is_pct):
            if v is None or not isinstance(v, (int, float)) or isinstance(v, bool):
                return "#e6edf3"
            if v > 0.6:  return "#f85149"
            if v > 0.3:  return "#e3b341"
            return "#3fb950"

        rows_html = ""
        last_cat  = None
        for label, val, is_pct, cat in kpis:
            if cat != last_cat:
                header = "Simulation Metrics" if cat == "KPI" else "Configuration"
                rows_html += f"""
                <tr>
                  <td colspan="2" style="padding:10px 10px 4px;font-size:10px;font-weight:700;
                      color:#6e7681;text-transform:uppercase;letter-spacing:.07em;
                      border-top:1px solid #21262d;">{header}</td>
                </tr>"""
                last_cat = cat

            fmted = _fmt(val, is_pct)
            color = _risk_color(val, is_pct) if cat == "KPI" else "#e6edf3"
            rows_html += f"""
            <tr style="border-bottom:1px solid #161b22;">
              <td style="padding:7px 10px;color:#8b949e;font-size:13px;">{label}</td>
              <td style="padding:7px 10px;font-size:13px;font-weight:600;
                         color:{color};text-align:right;">{fmted}</td>
            </tr>"""

        _section_heading("Results Table", "#8b949e")
        tbl_col, chart_col = st.columns([1, 1], gap="large")

        with tbl_col:
            st.markdown(f"""
            {_TABLER_CDN}
            <table style="width:100%;border-collapse:collapse;font-size:13px;
                          background:#0d1117;border-radius:8px;overflow:hidden;">
              <thead>
                <tr style="border-bottom:2px solid #21262d;">
                  <th style="text-align:left;padding:9px 10px;color:#6e7681;">KPI</th>
                  <th style="text-align:right;padding:9px 10px;color:#e6edf3;">Value</th>
                </tr>
              </thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)

        with chart_col:
            _section_heading("Infection Timeline", "#8b949e")
            import plotly.graph_objects as go
            fig = go.Figure()
            if "tick" in df.columns:
                x = df["tick"]
            else:
                x = list(range(1, len(df) + 1))
            if "total" in df.columns:
                fig.add_trace(go.Scatter(
                    x=x, y=df["total"],
                    mode="lines", name="Compromised",
                    line=dict(color="#f85149", width=2),
                    fill="tozeroy", fillcolor="rgba(248,81,73,0.10)",
                ))

            fig.update_layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3", size=12),
                xaxis=dict(title="Tick", gridcolor="#21262d"),
                yaxis=dict(title="Agents", gridcolor="#21262d"),
                legend=dict(bgcolor="#161b22", bordercolor="#21262d"),
                margin=dict(l=20, r=20, t=10, b=20),
                height=360,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        with st.expander("Full history", expanded=False):
            df_display = df.copy()
            if "tick" in df_display.columns:
                df_display = df_display.set_index("tick")
            df_display = df_display.loc[:, ~df_display.columns.duplicated()]
            subset_cols = [c for c in ["infected", "total"] if c in df_display.columns]
            if subset_cols:
                styled = df_display.style.background_gradient(cmap="Reds", subset=subset_cols)
                st.dataframe(styled, use_container_width=True)
            else:
                st.dataframe(df_display, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", data=csv,
                               file_name="cybertwin_live.csv", mime="text/csv")


if __name__ == "__main__":
    show()