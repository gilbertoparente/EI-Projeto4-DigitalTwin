import streamlit as st
from ui.components.config_builder import build_simulation_config
from ui.api_client import start_simulation


def _alert(msg: str, kind: str = "info"):
    styles = {
        "success": ("#0d2b1d", "#1a6e2d", "#3fb950", "✅"),
        "error":   ("#3d0f0f", "#7a2020", "#f85149", "❌"),
        "warning": ("#2a1700", "#5a3500", "#e3b341", "⚠️"),
        "info":    ("#1a2a4a", "#2d5096", "#58a6ff", "ℹ️"),
    }
    bg, border, color, icon = styles.get(kind, styles["info"])
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:10px;background:{bg};
                        border:1px solid {border};border-radius:8px;padding:10px 14px;margin:.5rem 0;">
              <span style="color:{color};font-size:16px">{icon}</span>
              <span style="color:{color};font-size:13px;">{msg}</span>
            </div>""",
        unsafe_allow_html=True,
    )


def _breach_probability(risk: float, awareness: float, education: str,
                        mfa: bool, training: float, attack_type: str,
                        click_rate: float) -> float:
    EDUCATION_MOD = {
        "High School": 0.8,
        "Bachelor's Degree": 1.0,
        "Master's / PhD": 1.2,
    }
    edu_mod = EDUCATION_MOD.get(education, 1.0)
    eff_awareness = min(1.0, awareness * edu_mod + training * 0.2)

    base_prob = risk * (1 - eff_awareness)
    avg_trust = 0.65
    p_click = min(1.0, base_prob + 0.4 * avg_trust)

    if attack_type == "Spear Phishing":
        p_click = min(1.0, p_click + 0.2)

    p_click = p_click * click_rate

    if mfa:
        p_click = p_click * 0.10

    return round(p_click, 3)


def show():
    st.markdown("""
    <h1 style='margin-bottom:.25rem'>Experiments</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Configure the organization, attack vector and defenses before initializing the Digital Twin.
    </p>
    """, unsafe_allow_html=True)

    config = build_simulation_config()

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        launch = st.button(
            "🚀 Initialize Digital Twin Engine",
            use_container_width=True,
            type="primary",
        )
    with col_info:
        total_agents = sum(len(d["agents"]) for d in config["organization"]["departments"])
        st.markdown(
            f"<p style='color:#6e7681; font-size:13px; margin-top:.6rem'>"
            f"Ready to create <strong style='color:#e6edf3'>{total_agents} agents</strong> "
            f"across <strong style='color:#e6edf3'>"
            f"{len(config['organization']['departments'])} department(s)</strong>.</p>",
            unsafe_allow_html=True,
        )

    if launch:
        with st.spinner("Sending configuration to server..."):
            result = start_simulation(config)

        if "error" in result:
            _alert(f"Failed to start simulation: {result['error']}", "error")
        else:
            _alert("Simulation initialized successfully!", "success")
            st.session_state["current_config"] = config

            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Agents created",  result.get("agents", 0))
            m2.metric("Graph edges",     result.get("edges", 0))
            m3.metric("Attack type",     config["attack"]["type"])
            m4.metric("MFA",             "Enabled ✅" if config["defense"]["mfa"] else "Disabled ❌")

            st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size:12px;font-weight:600;color:#8b949e;"
                "text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem'>"
                "Estimated breach probability per department</p>",
                unsafe_allow_html=True,
            )

            depts = config["organization"]["departments"]
            cols = st.columns(len(depts)) if len(depts) <= 4 else st.columns(4)
            attack_type = config["attack"]["type"]
            click_rate  = config["attack"].get("click_rate", 0.5)
            mfa_on      = config["defense"]["mfa"]
            training    = config["defense"]["training"]

            for idx, dept in enumerate(depts):
                col = cols[idx % len(cols)]
                agents = dept.get("agents", [])
                if not agents:
                    continue
                sample = agents[0]
                p = _breach_probability(
                    risk=sample["risk_propensity"],
                    awareness=sample["awareness_level"],
                    education=sample["education_level"],
                    mfa=mfa_on,
                    training=training,
                    attack_type=attack_type,
                    click_rate=click_rate,
                )
                pct = round(p * 100, 1)
                color = "#f85149" if pct > 30 else "#e3b341" if pct > 10 else "#3fb950"
                col.markdown(
                    f"""<div style="background:#161b22;border:1px solid #21262d;
                                   border-radius:8px;padding:.75rem 1rem;text-align:center;">
                          <div style="font-size:11px;color:#8b949e;margin-bottom:4px;
                                      text-transform:uppercase;letter-spacing:.05em;">
                            {dept['name']}
                          </div>
                          <div style="font-size:28px;font-weight:700;color:{color};">
                            {pct}%
                          </div>
                          <div style="font-size:11px;color:#6e7681;margin-top:2px;">
                            per agent / tick
                          </div>
                        </div>""",
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    show()