import streamlit as st
import pandas as pd
import time
import io
from ui.api_client import (
    start_scenarios, step_scenarios, get_scenarios_status, get_scenarios_compare,
)
from ui.components.config_builder import build_simulation_config

_TABLER_CDN = (
    "<link rel='stylesheet' "
    "href='https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css'>"
)


def _generate_pdf_report(compare_data: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER
        import datetime
    except ImportError:
        return b""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                  fontSize=20, spaceAfter=6, alignment=TA_CENTER)
    sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
                                  fontSize=10, alignment=TA_CENTER, spaceAfter=16)
    section_style = ParagraphStyle("section", parent=styles["Heading2"],
                                    fontSize=13, spaceBefore=16, spaceAfter=8)

    a = compare_data.get("scenario_a", {})
    b = compare_data.get("scenario_b", {})
    hist_a = compare_data.get("history_a", [])
    hist_b = compare_data.get("history_b", [])

    story = []
    story.append(Paragraph("CyberTwin — Scenario Comparison Report", title_style))
    story.append(Paragraph(
        f"Generated on {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e1e4e8")))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Scenario Configuration", section_style))
    cfg_data = [
        ["Parameter", "Scenario A", "Scenario B"],
        ["Attack Type", a.get("attack_type","—"), b.get("attack_type","—")],
        ["MFA", "Enabled" if a.get("mfa") else "Disabled", "Enabled" if b.get("mfa") else "Disabled"],
        ["Training", f"{a.get('training',0):.0%}", f"{b.get('training',0):.0%}"],
        ["Segmentation", f"{a.get('segmentation',0):.0%}", f"{b.get('segmentation',0):.0%}"],
        ["No. of Agents", str(a.get("n_agents",0)), str(b.get("n_agents",0))],
        ["Ticks run", str(a.get("ticks_run",0)), str(b.get("ticks_run",0))],
    ]
    _tbl_style = [
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0366d6")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#e1e4e8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f6f8fa")]),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING", (0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]
    t = Table(cfg_data, colWidths=[5*cm,5*cm,5*cm])
    t.setStyle(TableStyle(_tbl_style))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Final Results", section_style))
    def _fp(v): return f"{v*100:.1f}%" if v is not None else "—"
    def _fd(va, vb):
        if va is None or vb is None: return "—"
        d = (va or 0) - (vb or 0)
        return f"{d*100:+.1f}%" if isinstance(va, float) else f"{d:+d}"

    res_data = [
        ["KPI","Scenario A","Scenario B","Δ (A − B)"],
        ["Infection Rate",          _fp(a.get("infection_rate")),   _fp(b.get("infection_rate")),   _fd(a.get("infection_rate"),b.get("infection_rate"))],
        ["Click Rate",              _fp(a.get("click_rate")),       _fp(b.get("click_rate")),       _fd(a.get("click_rate"),b.get("click_rate"))],
        ["Open Rate",               _fp(a.get("open_rate")),        _fp(b.get("open_rate")),        _fd(a.get("open_rate"),b.get("open_rate"))],
        ["Click→Infected Conversion",_fp(a.get("conversion_rate")), _fp(b.get("conversion_rate")), _fd(a.get("conversion_rate"),b.get("conversion_rate"))],
        ["Infection Prob. / Tick",  _fp(a.get("infection_probability_per_tick")), _fp(b.get("infection_probability_per_tick")), _fd(a.get("infection_probability_per_tick"),b.get("infection_probability_per_tick"))],
        ["Compromised (final)",     str(a.get("final_compromised",0)), str(b.get("final_compromised",0)), str((a.get("final_compromised",0) or 0)-(b.get("final_compromised",0) or 0))],
        ["MTTD (ticks)",            str(a.get("mttd") or "N/A"),   str(b.get("mttd") or "N/A"),   "—"],
    ]
    res_tbl_style = [
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#24292e")),
        ("TEXTCOLOR", (0,0),(-1,0),colors.white),
        ("FONTNAME",  (0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1),9),
        ("GRID",      (0,0),(-1,-1),0.5,colors.HexColor("#e1e4e8")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8fa")]),
        ("ALIGN",     (1,0),(-1,-1),"CENTER"),
        ("VALIGN",    (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]
    rt = Table(res_data, colWidths=[5.5*cm,3.2*cm,3.2*cm,3*cm])
    rt.setStyle(TableStyle(res_tbl_style))
    story.append(rt)

    if hist_a and hist_b:
        story.append(Spacer(1,0.5*cm))
        story.append(Paragraph("Timeline by Tick", section_style))
        tick_rows = [["Tick","A — Compromised","A — Infected","B — Compromised","B — Infected"]]
        for idx in range(max(len(hist_a),len(hist_b))):
            ra = hist_a[idx] if idx < len(hist_a) else {}
            rb = hist_b[idx] if idx < len(hist_b) else {}
            tick_rows.append([
                str(ra.get("tick",idx+1)),
                str(ra.get("total_compromised","—")), str(ra.get("infected","—")),
                str(rb.get("total_compromised","—")), str(rb.get("infected","—")),
            ])
        tt = Table(tick_rows, colWidths=[2*cm,3.5*cm,3.5*cm,3.5*cm,3.5*cm])
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#586069")),
            ("TEXTCOLOR", (0,0),(-1,0),colors.white),
            ("FONTNAME",  (0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",  (0,0),(-1,-1),8),
            ("GRID",      (0,0),(-1,-1),0.3,colors.HexColor("#e1e4e8")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8fa")]),
            ("ALIGN",     (0,0),(-1,-1),"CENTER"),
            ("VALIGN",    (0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        story.append(tt)

    doc.build(story)
    return buf.getvalue()


def _section_heading(label: str, color: str = "#58a6ff"):
    st.markdown(
        f"""<div style="border-left:3px solid {color}; padding-left:12px;
                        margin-bottom:.75rem; border-radius:0;">
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
                        border:1px solid {border};border-radius:8px;
                        padding:10px 14px;margin:.5rem 0;">
              <i class="ti {icon}" style="color:{color};font-size:16px;flex-shrink:0"
                 aria-hidden="true"></i>
              <span style="color:{color};font-size:13px;">{msg}</span>
            </div>""",
        unsafe_allow_html=True,
    )


def _highlight(value_a, value_b, lower_better: bool = True):
    if value_a is None or value_b is None:
        return "", ""
    base = "padding:6px 10px;border-radius:6px;"
    win  = base + "background:#1a3a1a;color:#3fb950;font-weight:600;"
    lose = base + "color:#8b949e;"
    tie  = base + "color:#e6edf3;"
    if lower_better:
        if value_a < value_b: return win, lose
        if value_b < value_a: return lose, win
    else:
        if value_a > value_b: return win, lose
        if value_b > value_a: return lose, win
    return tie, tie


def _render_comparison_table(a: dict, b: dict):
    kpis = [
        ("Infection Rate",               "infection_rate",                True,  True),
        ("Click Rate",                   "click_rate",                    True,  True),
        ("Open Rate",                    "open_rate",                     True,  True),
        ("Click→Infected Conversion",    "conversion_rate",               True,  True),
        ("Infection Prob. / Tick",       "infection_probability_per_tick",True,  True),
        ("Final compromised",            "final_compromised",             False, True),
        ("Max. Compromised",             "max_compromised",               False, True),
        ("MTTD (ticks)",                 "mttd",                          False, True),
        ("Attack Type",                  "attack_type",                   False, False),
        ("MFA",                          "mfa",                           False, False),
        ("Training",                     "training",                      False, False),
        ("Segmentation",                 "segmentation",                  False, False),
        ("Ticks run",                    "ticks_run",                     False, False),
        ("No. of Agents",                "n_agents",                      False, False),
    ]

    rows_html = ""
    for label, key, is_pct, has_highlight in kpis:
        va = a.get(key)
        vb = b.get(key)

        def fmt(v):
            if v is None: return "—"
            if isinstance(v, bool): return "Enabled" if v else "Disabled"
            if is_pct: return f"{v*100:.1f}%"
            if isinstance(v, float): return f"{v:.4f}"
            return str(v)

        sa, sb = _highlight(va, vb, lower_better=True) if has_highlight else ("", "")
        style_a = f"style='{sa}'" if sa else ""
        style_b = f"style='{sb}'" if sb else ""

        rows_html += f"""
        <tr>
          <td style="padding:6px 10px;color:#8b949e;font-size:13px">{label}</td>
          <td {style_a}>{fmt(va)}</td>
          <td {style_b}>{fmt(vb)}</td>
        </tr>"""

    st.markdown(f"""
    {_TABLER_CDN}
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <thead>
        <tr style="border-bottom:1px solid #21262d">
          <th style="text-align:left;padding:8px 10px;color:#6e7681">KPI</th>
          <th style="text-align:center;padding:8px 10px;color:#58a6ff">
            <span style="display:inline-flex;align-items:center;gap:6px;">
              <span style="width:8px;height:8px;border-radius:50%;background:#58a6ff;"></span>
              Scenario A
            </span>
          </th>
          <th style="text-align:center;padding:8px 10px;color:#f85149">
            <span style="display:inline-flex;align-items:center;gap:6px;">
              <span style="width:8px;height:8px;border-radius:50%;background:#f85149;"></span>
              Scenario B
            </span>
          </th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)


def _render_config_summary_cmp(label: str, config: dict, color: str):
    if not config:
        return
    depts   = config.get("organization", {}).get("departments", [])
    attack  = config.get("attack", {})
    defense = config.get("defense", {})

    st.markdown(
        f"""<div style='font-size:11px;font-weight:700;color:{color};text-transform:uppercase;
                        letter-spacing:.07em;margin-bottom:.5rem;display:flex;align-items:center;gap:6px;'>
              <span style='width:7px;height:7px;border-radius:50%;background:{color};'></span>
              {label}
            </div>""",
        unsafe_allow_html=True,
    )

    if depts:
        dept_cols = st.columns(min(len(depts), 3))
        for i, dept in enumerate(depts[:3]):
            agents = dept.get("agents", [])
            sample = agents[0] if agents else {}
            risk_raw = sample.get("risk_propensity", 0.5)
            aw_raw   = sample.get("awareness_level", 0.5)
            risk_color  = "#f85149" if risk_raw > 0.6 else "#e3b341" if risk_raw > 0.3 else "#3fb950"
            aware_color = "#3fb950" if aw_raw > 0.6 else "#e3b341" if aw_raw > 0.3 else "#f85149"
            with dept_cols[i]:
                st.markdown(
                    f"""<div style="background:#0d1117;border:1px solid #21262d;
                                   border-radius:6px;padding:.5rem .75rem;margin-bottom:.4rem;">
                          <div style="font-size:10px;color:#8b949e;text-transform:uppercase;
                                      letter-spacing:.04em;margin-bottom:4px;">{dept['name']}</div>
                          <div style="font-size:11px;color:#e6edf3;">👥 {len(agents)} agents</div>
                          <div style="font-size:11px;color:{risk_color};">risk {int(risk_raw*100)}%</div>
                          <div style="font-size:11px;color:{aware_color};">aware {int(aw_raw*100)}%</div>
                        </div>""",
                    unsafe_allow_html=True,
                )

    atk_type    = attack.get("type", "—")
    click_rate  = attack.get("click_rate", 0)
    mfa         = defense.get("mfa", False)
    training    = defense.get("training", 0)
    segmentation = defense.get("segmentation", 0)
    mfa_color   = "#3fb950" if mfa else "#e3b341"
    atk_color   = "#f85149" if atk_type == "Spear Phishing" else "#e3b341"
    st.markdown(
        f"""<div style="background:#0d1117;border:1px solid #21262d;
                       border-radius:6px;padding:.5rem .75rem;font-size:11px;">
              <span style="color:{atk_color};font-weight:600;">{atk_type}</span>
              <span style="color:#6e7681;"> · intensity {int(click_rate*100)}%</span>
              <span style="color:{mfa_color};margin-left:8px;">
                {'🔒 MFA' if mfa else '⚠️ no MFA'}
              </span>
              <span style="color:#8b949e;"> · training {int(training*100)}%
                · seg. {int(segmentation*100)}%</span>
            </div>""",
        unsafe_allow_html=True,
    )


def show():
    st.markdown("""
    <h1 style='margin-bottom:.25rem'>Scenario Comparison</h1>
    <p style='color:#8b949e;font-size:14px;margin-bottom:1.5rem'>
      Configure two scenarios, run them simultaneously and compare results.
    </p>
    """, unsafe_allow_html=True)

    tab_cfg, tab_run, tab_result = st.tabs(["Configuration", "Execution", "Results"])

    with tab_cfg:
        col_a, col_sep, col_b = st.columns([10, 1, 10])

        with col_a:
            st.markdown(f"""{_TABLER_CDN}
            <div style='background:#0d2035;border:1px solid #1f4068;border-radius:8px;
                        padding:.7rem 1.1rem;margin-bottom:1.25rem;
                        display:flex;align-items:center;gap:8px;'>
              <span style='width:10px;height:10px;border-radius:50%;background:#58a6ff;
                           flex-shrink:0;'></span>
              <span style='color:#58a6ff;font-weight:700;font-size:14px;
                           text-transform:uppercase;letter-spacing:.07em;'>Scenario A</span>
            </div>""", unsafe_allow_html=True)
            config_a = build_simulation_config(prefix="cmp_a_")

        with col_sep:
            st.markdown(
                "<div style='width:1px;background:#21262d;min-height:600px;margin:0 auto;'></div>",
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(f"""{_TABLER_CDN}
            <div style='background:#2d0d0d;border:1px solid #6b1f1f;border-radius:8px;
                        padding:.7rem 1.1rem;margin-bottom:1.25rem;
                        display:flex;align-items:center;gap:8px;'>
              <span style='width:10px;height:10px;border-radius:50%;background:#f85149;
                           flex-shrink:0;'></span>
              <span style='color:#f85149;font-weight:700;font-size:14px;
                           text-transform:uppercase;letter-spacing:.07em;'>Scenario B</span>
            </div>""", unsafe_allow_html=True)
            config_b = build_simulation_config(prefix="cmp_b_")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Initialize both scenarios", type="primary", use_container_width=True):
            with st.spinner("Initializing…"):
                result = start_scenarios(config_a, config_b)
            if "error" in result:
                _alert(f"Error: {result['error']}", "error")
            else:
                _alert(
                    f"{result.get('status')} — "
                    f"A: {result.get('scenario_a_agents')} agents | "
                    f"B: {result.get('scenario_b_agents')} agents",
                    "success"
                )
                st.session_state["scenarios_ready"] = True
                st.session_state["current_config_cmp_a"] = config_a
                st.session_state["current_config_cmp_b"] = config_b
                st.session_state.pop("cmp_history", None)

    with tab_run:
        status = get_scenarios_status()
        if status.get("status") == "idle":
            _alert("Scenarios not started. Configure in the <strong>Configuration</strong> tab.", "warning")
            return

        sa = status.get("scenario_a", {})
        sb = status.get("scenario_b", {})

        m_cols = st.columns(4)

        with m_cols[0]:
            st.markdown(
                f"""{_TABLER_CDN}<p style='font-size:11px;color:#58a6ff;margin-bottom:0;
                    display:flex;align-items:center;gap:5px;'>
                  <span style='width:6px;height:6px;border-radius:50%;background:#58a6ff;'></span>
                  Tick A</p>""", unsafe_allow_html=True)
            st.metric("Tick A", sa.get("tick", 0), label_visibility="collapsed")

        with m_cols[1]:
            st.markdown(
                f"""<p style='font-size:11px;color:#58a6ff;margin-bottom:0;
                    display:flex;align-items:center;gap:5px;'>
                  <span style='width:6px;height:6px;border-radius:50%;background:#58a6ff;'></span>
                  Compromised A</p>""", unsafe_allow_html=True)
            st.metric("Compromised A", sa.get("compromised", 0),
                      delta=f"{round(sa.get('compromised',0)/max(sa.get('agents',1),1)*100,1)}%",
                      label_visibility="collapsed")

        with m_cols[2]:
            st.markdown(
                f"""<p style='font-size:11px;color:#f85149;margin-bottom:0;
                    display:flex;align-items:center;gap:5px;'>
                  <span style='width:6px;height:6px;border-radius:50%;background:#f85149;'></span>
                  Tick B</p>""", unsafe_allow_html=True)
            st.metric("Tick B", sb.get("tick", 0), label_visibility="collapsed")

        with m_cols[3]:
            st.markdown(
                f"""<p style='font-size:11px;color:#f85149;margin-bottom:0;
                    display:flex;align-items:center;gap:5px;'>
                  <span style='width:6px;height:6px;border-radius:50%;background:#f85149;'></span>
                  Compromised B</p>""", unsafe_allow_html=True)
            st.metric("Compromised B", sb.get("compromised", 0),
                      delta=f"{round(sb.get('compromised',0)/max(sb.get('agents',1),1)*100,1)}%",
                      label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        cfg_a = st.session_state.get("current_config_cmp_a", {})
        cfg_b = st.session_state.get("current_config_cmp_b", {})
        if cfg_a or cfg_b:
            sum_a, sum_b = st.columns(2)
            with sum_a:
                _render_config_summary_cmp("Scenario A", cfg_a, "#58a6ff")
            with sum_b:
                _render_config_summary_cmp("Scenario B", cfg_b, "#f85149")
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
                key="cmp_n_steps",
            )
        with ctrl2:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            run_btn = st.button(f"▶ Run {n_steps} steps", type="primary", use_container_width=True)
        with ctrl3:
            agents_a = sa.get("agents", 0)
            agents_b = sb.get("agents", 0)
            max_agents = max(agents_a, agents_b, 1)
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            auto_btn = st.button("⏩ Run until done", use_container_width=True,
                                 help="Runs until all agents in both scenarios are compromised or 1000 ticks pass.")

        st.markdown("</div>", unsafe_allow_html=True)

        chart_placeholder  = st.empty()
        status_placeholder = st.empty()

        def _do_steps(n, delay=0.0):
            data = step_scenarios(n)
            if "error" in data:
                _alert(data["error"], "error")
                return
            st.session_state["cmp_history"] = data

        def _render_live_chart():
            data = st.session_state.get("cmp_history")
            if not data:
                return
            hist_a = data.get("scenario_a", [])
            hist_b = data.get("scenario_b", [])
            if not hist_a or not hist_b:
                return
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[h["tick"] for h in hist_a],
                y=[h["total_compromised"] for h in hist_a],
                mode="lines+markers", name="Scenario A",
                line=dict(color="#58a6ff", width=2), marker=dict(size=5),
            ))
            fig.add_trace(go.Scatter(
                x=[h["tick"] for h in hist_b],
                y=[h["total_compromised"] for h in hist_b],
                mode="lines+markers", name="Scenario B",
                line=dict(color="#f85149", width=2), marker=dict(size=5),
            ))
            fig.update_layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3", size=12),
                xaxis=dict(title="Tick", gridcolor="#21262d"),
                yaxis=dict(title="Compromised", gridcolor="#21262d"),
                legend=dict(bgcolor="#161b22", bordercolor="#21262d"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
            )
            chart_placeholder.plotly_chart(fig, use_container_width=True)

        if run_btn:
            with st.spinner(f"Running {n_steps} steps…"):
                _do_steps(n_steps)
            _render_live_chart()

        if auto_btn:
            prog = st.progress(0, text="Running until done…")
            tick_count = 0
            max_ticks  = 1000
            while tick_count < max_ticks:
                _do_steps(1)
                hist = st.session_state.get("cmp_history", {})
                hist_a_now = hist.get("scenario_a", [])
                hist_b_now = hist.get("scenario_b", [])
                comp_a = hist_a_now[-1].get("total_compromised", 0) if hist_a_now else 0
                comp_b = hist_b_now[-1].get("total_compromised", 0) if hist_b_now else 0
                tick_count += 1
                pct = min(
                    max(comp_a / max(agents_a, 1), comp_b / max(agents_b, 1)),
                    tick_count / max_ticks,
                )
                prog.progress(pct, text=f"Tick {tick_count} — A: {comp_a}/{agents_a} · B: {comp_b}/{agents_b}")
                if comp_a >= agents_a and comp_b >= agents_b:
                    break
            prog.empty()
            _render_live_chart()

        if "cmp_history" in st.session_state and not run_btn and not auto_btn:
            _render_live_chart()

    with tab_result:
        compare = get_scenarios_compare()
        if "error" in compare:
            _alert("Run steps in the <strong>Execution</strong> tab to see results.", "info")
            return

        a = compare.get("scenario_a", {})
        b = compare.get("scenario_b", {})

        _section_heading("Comparison Table", "#8b949e")
        _render_comparison_table(a, b)

        hist_a = compare.get("history_a", [])
        hist_b = compare.get("history_b", [])
        if hist_a and hist_b:
            st.markdown("<br>", unsafe_allow_html=True)
            _section_heading("Infection Timeline", "#8b949e")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[h["tick"] for h in hist_a],
                y=[h["total_compromised"] for h in hist_a],
                mode="lines", name="Scenario A",
                line=dict(color="#58a6ff", width=2),
                fill="tozeroy", fillcolor="rgba(88,166,255,0.1)",
            ))
            fig.add_trace(go.Scatter(
                x=[h["tick"] for h in hist_b],
                y=[h["total_compromised"] for h in hist_b],
                mode="lines", name="Scenario B",
                line=dict(color="#f85149", width=2),
                fill="tozeroy", fillcolor="rgba(248,81,73,0.1)",
            ))
            fig.update_layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3"), height=340,
                xaxis=dict(title="Tick", gridcolor="#21262d"),
                yaxis=dict(title="Compromised", gridcolor="#21262d"),
                legend=dict(bgcolor="#161b22", bordercolor="#21262d"),
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        exp1, exp2 = st.columns(2)
        with exp1:
            if hist_a and hist_b:
                df_a = pd.DataFrame(hist_a)
                df_a.columns = [f"A_{c}" for c in df_a.columns]
                df_b = pd.DataFrame(hist_b)
                df_b.columns = [f"B_{c}" for c in df_b.columns]
                csv = pd.concat([df_a, df_b], axis=1).to_csv(index=False).encode("utf-8")
                st.download_button("Export CSV", data=csv,
                                   file_name="scenario_comparison.csv",
                                   mime="text/csv", use_container_width=True)
        with exp2:
            pdf_bytes = _generate_pdf_report(compare)
            if pdf_bytes:
                st.download_button("Export PDF", data=pdf_bytes,
                                   file_name="comparison_report.pdf",
                                   mime="application/pdf", use_container_width=True)