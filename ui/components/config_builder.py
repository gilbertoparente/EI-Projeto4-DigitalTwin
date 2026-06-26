import json
import streamlit as st

EDUCATION_LEVELS = ["High School", "Bachelor's Degree", "Master's / PhD"]

EDUCATION_AWARENESS_MOD = {
    "High School":       0.8,
    "Bachelor's Degree": 1.0,
    "Master's / PhD":    1.2,
}

DEPARTMENTS_FILE = "saved_departments.json"

BUILTIN_PRESETS = {
    "small_company": {
        "name": "Small Company",
        "departments": [
            {"name": "IT", "agents": [{"hierarchy_level": 2, "risk_propensity": 0.3,
              "awareness_level": 0.8, "education_level": "Bachelor's Degree"}]},
            {"name": "Sales", "agents": [{"hierarchy_level": 1, "risk_propensity": 0.6,
              "awareness_level": 0.4, "education_level": "High School"}]},
        ],
    },
    "bank": {
        "name": "Bank / Financial",
        "departments": [
            {"name": "Compliance", "agents": [{"hierarchy_level": 3, "risk_propensity": 0.2,
              "awareness_level": 0.9, "education_level": "Master's / PhD"}]},
            {"name": "Operations", "agents": [{"hierarchy_level": 1, "risk_propensity": 0.5,
              "awareness_level": 0.5, "education_level": "Bachelor's Degree"}]},
            {"name": "Customer Support", "agents": [{"hierarchy_level": 1, "risk_propensity": 0.7,
              "awareness_level": 0.3, "education_level": "High School"}]},
        ],
    },
    "tech_startup": {
        "name": "Tech Startup",
        "departments": [
            {"name": "Engineering", "agents": [{"hierarchy_level": 2, "risk_propensity": 0.25,
              "awareness_level": 0.85, "education_level": "Master's / PhD"}]},
            {"name": "Marketing", "agents": [{"hierarchy_level": 1, "risk_propensity": 0.55,
              "awareness_level": 0.45, "education_level": "Bachelor's Degree"}]},
        ],
    },
}


def _load_saved_departments() -> dict:
    try:
        with open(DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_departments_to_file(data: dict):
    with open(DEPARTMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _all_presets() -> dict:
    merged = dict(BUILTIN_PRESETS)
    merged.update(_load_saved_departments())
    return merged


def _flush_pending_preset(prefix: str):
    pending_key = f"_pending_preset_{prefix}"
    if pending_key not in st.session_state:
        return
    pending     = st.session_state.pop(pending_key)
    departments = pending.get("departments", [])
    if not departments:
        return

    n = max(1, min(6, len(departments)))
    st.session_state[f"{prefix}n_depts"] = n

    for i, dept_data in enumerate(departments[:6]):
        agents = dept_data.get("agents", [])
        first  = agents[0] if agents else {}
        st.session_state[f"{prefix}dept_name_{i}"] = dept_data.get("name", f"Dept_{i+1}")
        st.session_state[f"{prefix}n_agents_{i}"]  = max(2, len(agents)) if agents else 5
        st.session_state[f"{prefix}risk_{i}"]      = float(first.get("risk_propensity", 0.5))
        st.session_state[f"{prefix}aware_{i}"]     = float(first.get("awareness_level", 0.5))
        st.session_state[f"{prefix}hier_{i}"]      = int(first.get("hierarchy_level", 1))
        st.session_state[f"{prefix}edu_{i}"]       = first.get("education_level", "Bachelor's Degree")


def _schedule_preset(prefix: str, departments: list):
    st.session_state[f"_pending_preset_{prefix}"] = {
        "departments": departments,
    }
    st.rerun()


def _section(label: str, color: str = "#58a6ff"):
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:10px;margin:1.25rem 0 .75rem;">
              <div style="width:3px;height:18px;background:{color};
                          border-radius:2px;flex-shrink:0;"></div>
              <span style="font-size:12px;font-weight:600;color:{color};
                           text-transform:uppercase;letter-spacing:.07em;">{label}</span>
              <div style="flex:1;height:1px;background:#21262d;"></div>
            </div>""",
        unsafe_allow_html=True,
    )


def _preset_card(key: str, preset: dict, prefix: str, saved_only: dict):
    depts      = preset.get("departments", [])
    dept_names = ", ".join(d.get("name", "?") for d in depts[:3])
    if len(depts) > 3:
        dept_names += f" +{len(depts)-3}"

    sample     = depts[0].get("agents", [{}])[0] if depts else {}
    risk_raw   = sample.get("risk_propensity", 0.5)
    aware_raw  = sample.get("awareness_level", 0.5)
    risk_color  = "#f85149" if risk_raw > 0.6 else "#e3b341" if risk_raw > 0.3 else "#3fb950"
    aware_color = "#3fb950" if aware_raw > 0.6 else "#e3b341" if aware_raw > 0.3 else "#f85149"

    st.markdown(
        f"""<div style="background:#0d1117;border:1px solid #21262d;border-radius:8px;
                        padding:.7rem .9rem;margin-bottom:.3rem;">
              <div style="font-size:12px;font-weight:600;color:#e6edf3;margin-bottom:3px;">
                {preset['name']}
              </div>
              <div style="font-size:11px;color:#6e7681;margin-bottom:5px;">{dept_names}</div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <span style="font-size:11px;color:{risk_color};">risk {int(risk_raw*100)}%</span>
                <span style="font-size:11px;color:{aware_color};">aware {int(aware_raw*100)}%</span>
                <span style="font-size:11px;color:#8b949e;">{len(depts)} dept</span>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )

    is_builtin = key in BUILTIN_PRESETS
    if is_builtin:
        if st.button("Apply", key=f"{prefix}apply_{key}", use_container_width=True):
            if depts:
                _schedule_preset(prefix, depts)
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("Apply", key=f"{prefix}apply_{key}", use_container_width=True):
                if depts:
                    _schedule_preset(prefix, depts)
        with c2:
            if st.button("🗑", key=f"{prefix}del_{key}", use_container_width=True,
                         help="Remove preset"):
                saved_only.pop(key, None)
                _save_departments_to_file(saved_only)
                st.rerun()


def build_simulation_config(prefix: str = "") -> dict:
    _flush_pending_preset(prefix)

    all_presets = _all_presets()
    saved_only  = _load_saved_departments()

    _section("Organization", "#58a6ff")
    col_editor, col_presets = st.columns([3, 1], gap="large")

    with col_editor:
        n_depts = st.number_input(
            "Number of departments",
            min_value=1, max_value=6, value=2,
            key=f"{prefix}n_depts",
            help="How many distinct departments the simulated organization will have.",
        )

        departments = []
        for i in range(int(n_depts)):
            st.markdown(
                f"""<div style="display:flex;align-items:center;gap:8px;margin:1.25rem 0 .6rem;">
                      <div style="background:#21262d;color:#8b949e;font-size:10px;font-weight:700;
                                  border-radius:4px;padding:2px 7px;letter-spacing:.05em;">
                        DEPT {i+1}
                      </div>
                      <div style="flex:1;height:1px;background:#21262d;"></div>
                    </div>""",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns([2, 1])
            with c1:
                name = st.text_input(
                    "Name", value=f"Dept_{i+1}",
                    key=f"{prefix}dept_name_{i}",
                )
            with c2:
                n_agents = st.number_input(
                    "Agents", min_value=2, max_value=50, value=5,
                    key=f"{prefix}n_agents_{i}",
                )

            a1, a2, a3, a4 = st.columns(4)
            with a1:
                risk = st.slider(
                    "Risk", 0.0, 1.0, 0.5, 0.05,
                    key=f"{prefix}risk_{i}",
                    help="Base probability of clicking a suspicious message.",
                )
            with a2:
                base_awareness = st.slider(
                    "Awareness", 0.0, 1.0, 0.5, 0.05,
                    key=f"{prefix}aware_{i}",
                    help="Cybersecurity literacy (before education modifier).",
                )
            with a3:
                hier = st.select_slider(
                    "Hierarchy", options=[1, 2, 3], value=1,
                    key=f"{prefix}hier_{i}",
                    help="1 = operational  2 = management  3 = executive",
                )
            with a4:
                education = st.selectbox(
                    "Education", EDUCATION_LEVELS, index=1,
                    key=f"{prefix}edu_{i}",
                    help="Modifies awareness: High School ×0.8 | BSc ×1.0 | MSc/PhD ×1.2",
                )

            edu_mod = EDUCATION_AWARENESS_MOD.get(education, 1.0)
            eff_aw  = min(1.0, base_awareness * edu_mod)
            st.caption(f"Effective awareness with {edu_mod:.1f}× modifier: **{eff_aw:.2f}**")

            departments.append({
                "name": name,
                "agents": [
                    {
                        "name":            f"User_{i+1}_{j+1}",
                        "hierarchy_level": hier,
                        "risk_propensity": risk,
                        "awareness_level": base_awareness,
                        "education_level": education,
                        "education":       education,
                    }
                    for j in range(int(n_agents))
                ],
            })

    with col_presets:
        _section("Presets", "#a371f7")

        new_name = st.text_input(
            "Save as…",
            placeholder="Preset name",
            key=f"{prefix}preset_name_input",
        )
        if st.button("💾 Save", key=f"{prefix}btn_save_preset", use_container_width=True):
            if not new_name.strip():
                st.warning("Enter a name.")
            else:
                k = new_name.strip().lower().replace(" ", "_")
                saved_only[k] = {"name": new_name.strip(), "departments": departments}
                _save_departments_to_file(saved_only)
                st.success("Saved!")
                st.rerun()

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        if all_presets:
            for key, preset in all_presets.items():
                _preset_card(key, preset, prefix, saved_only)
        else:
            st.markdown(
                "<p style='font-size:12px;color:#6e7681;'>No presets.</p>",
                unsafe_allow_html=True,
            )

    col_atk, col_def = st.columns(2, gap="large")

    with col_atk:
        _section("Attack Vector", "#f78166")

        attack_type = st.selectbox(
            "Attack type",
            ["Phishing", "Spear Phishing"],
            key=f"{prefix}attack_type",
            help="Phishing: random mass campaign.\nSpear Phishing: targets the highest-ranking agents.",
        )
        st.markdown(
            f"""<div style="background:#1a0f0a;border:1px solid #3d1a10;border-radius:6px;
                           padding:.6rem .9rem;margin:.5rem 0 1rem;font-size:12px;color:#c9a08a;">
                  {"Targets the 5 agents with the highest hierarchy level."
                   if attack_type == "Spear Phishing"
                   else "Reaches ~5% of the population randomly per tick."}
                </div>""",
            unsafe_allow_html=True,
        )
        click_rate = st.slider(
            "Base intensity", 0.0, 1.0, 0.5, 0.05,
            key=f"{prefix}click_rate",
            help="Scales the initial success probability before defenses apply.",
        )

    with col_def:
        _section("Defenses", "#3fb950")

        mfa = st.toggle(
            "MFA enabled", value=True,
            key=f"{prefix}mfa",
            help="Multi-Factor Authentication — blocks ~90% of access attempts even with stolen credentials.",
        )
        st.markdown(
            f"""<div style="background:{'#0d2b1d' if mfa else '#2a1700'};
                           border:1px solid {'#1a6e2d' if mfa else '#5a3500'};
                           border-radius:6px;padding:.5rem .9rem;margin:.25rem 0 .75rem;
                           font-size:12px;color:{'#3fb950' if mfa else '#e3b341'};">
                  {"MFA enabled — 90% reduction in compromise rate."
                   if mfa else "MFA disabled — compromised credentials = direct access."}
                </div>""",
            unsafe_allow_html=True,
        )
        training = st.slider(
            "Training effectiveness", 0.0, 1.0, 0.3, 0.05,
            key=f"{prefix}training",
            help="Awareness programs — increases agent awareness each tick.",
        )
        segmentation = st.slider(
            "Network segmentation", 0.0, 1.0, 0.5, 0.05,
            key=f"{prefix}segmentation",
            help="0 = flat network (free lateral movement).  1 = zero-trust.",
        )

    return {
        "organization": {"departments": departments},
        "attack":       {"type": attack_type, "click_rate": click_rate},
        "defense":      {"mfa": mfa, "training": training, "segmentation": segmentation},
        "attack_params": {
            "global_intensity":     click_rate,
            "global_training":      training,
            "spear_bonus":          0.2,
            "homophily_multiplier": 1.4,
        },
    }