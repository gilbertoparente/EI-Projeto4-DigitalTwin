import json
import streamlit as st

_TABLER_CDN = (
    "<link rel='stylesheet' "
    "href='https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css'>"
)

DEPARTMENTS_FILE = "saved_departments.json"


# ─────────────────────────────────────────────────────────────────────────────
# JSON helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_saved_departments() -> dict:
    try:
        with open(DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_departments_to_file(data: dict) -> None:
    with open(DEPARTMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────────────────────────────────────

def _section_card_open(label: str, color: str = "#58a6ff"):
    st.markdown(
        f"""{_TABLER_CDN}
            <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                        padding:1.25rem 1.5rem; margin-bottom:1rem;">
              <div style="border-left:3px solid {color}; padding-left:12px; margin-bottom:1rem;">
                <span style="font-size:11px; font-weight:600; color:{color};
                             text-transform:uppercase; letter-spacing:.06em;">{label}</span>
              </div>""",
        unsafe_allow_html=True,
    )


def _section_card_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Guardar todos os departamentos actuais como preset
# ─────────────────────────────────────────────────────────────────────────────

def _render_save_panel(prefix: str, departments: list):
    """Linha simples para guardar a config actual como preset."""
    saved = _load_saved_departments()
    col_name, col_btn = st.columns([3, 1])
    with col_name:
        preset_name = st.text_input(
            "Nome do preset",
            placeholder="Ex: Empresa_Media",
            key=f"{prefix}preset_name_input",
            label_visibility="collapsed",
        )
    with col_btn:
        if st.button("💾 Guardar", key=f"{prefix}btn_save_preset", use_container_width=True):
            if not preset_name.strip():
                st.warning("Introduz um nome.")
            elif not departments:
                st.warning("Não há departamentos para guardar.")
            else:
                key = preset_name.strip().lower().replace(" ", "_")
                saved[key] = {"name": preset_name.strip(), "departments": departments}
                _save_departments_to_file(saved)
                st.success(f"✅ **{preset_name}** guardado!")


# ─────────────────────────────────────────────────────────────────────────────
# Injectar preset nos session_state keys de um departamento específico
# ─────────────────────────────────────────────────────────────────────────────

def _inject_dept_preset(prefix: str, i: int, dept_data: dict):
    """
    Escreve directamente no session_state os valores do preset para o
    departamento i. Os widgets lêem session_state pelo key, por isso
    na próxima renderização aparecem já com os valores carregados.
    """
    agents = dept_data.get("agents", [])
    if not agents:
        return

    # Usa as métricas do primeiro agente (todos partilham os mesmos valores)
    first = agents[0]

    st.session_state[f"{prefix}dept_name_{i}"] = dept_data.get("name", f"Dept_{i+1}")
    st.session_state[f"{prefix}n_agents_{i}"] = len(agents)
    st.session_state[f"{prefix}risk_{i}"]     = float(first.get("risk_propensity", 0.5))
    st.session_state[f"{prefix}aware_{i}"]    = float(first.get("awareness_level", 0.5))
    st.session_state[f"{prefix}hier_{i}"]     = int(first.get("hierarchy_level", 1))


# ─────────────────────────────────────────────────────────────────────────────
# Função pública principal
# ─────────────────────────────────────────────────────────────────────────────

def build_simulation_config(prefix: str = "") -> dict:
    """
    Constrói o dicionário completo de configuração da simulação.
    prefix: string única quando a função é chamada mais do que uma vez na mesma página.
    """

    saved = _load_saved_departments()

    # ── Secção 1: Organização ─────────────────────────────────
    _section_card_open("Organização", "#58a6ff")
    n_depts = st.number_input(
        "Número de departamentos",
        min_value=1, max_value=6, value=2,
        key=f"{prefix}n_depts",
        help="Quantos departamentos distintos terá a organização simulada.",
    )
    _section_card_close()

    # ── Departamentos ─────────────────────────────────────────
    departments = []
    for i in range(int(n_depts)):
        with st.expander(f"Departamento {i + 1}", expanded=(i == 0)):

            # ── Carregar preset para este departamento ────────
            if saved:
                preset_options = {"— sem preset —": None}
                preset_options.update({v["name"]: k for k, v in saved.items()})

                selected_label = st.selectbox(
                    "Carregar preset",
                    options=list(preset_options.keys()),
                    key=f"{prefix}dept_preset_select_{i}",
                    help="Substitui as métricas deste departamento pelo preset seleccionado.",
                )
                selected_key = preset_options[selected_label]

                if selected_key is not None:
                    preset_entry = saved[selected_key]
                    # Um preset pode ter vários departamentos; usa o i-ésimo se existir,
                    # caso contrário usa sempre o primeiro.
                    dept_list = preset_entry.get("departments", [])
                    source_dept = dept_list[i] if i < len(dept_list) else (dept_list[0] if dept_list else None)

                    if source_dept and st.button(
                        f"↩ Aplicar \"{selected_label}\"",
                        key=f"{prefix}btn_apply_preset_{i}",
                    ):
                        _inject_dept_preset(prefix, i, source_dept)
                        st.rerun()

                st.markdown("<hr style='border-color:#21262d;margin:8px 0'>", unsafe_allow_html=True)

            # ── Campos do departamento ────────────────────────
            c1, c2 = st.columns([2, 1])
            with c1:
                name = st.text_input(
                    "Nome do departamento",
                    value=f"Dept_{i + 1}",
                    key=f"{prefix}dept_name_{i}",
                )
            with c2:
                n_agents = st.number_input(
                    "Nº de agentes",
                    min_value=2, max_value=50, value=5,
                    key=f"{prefix}n_agents_{i}",
                )

            dept_agents = []
            if n_agents > 0:
                st.markdown(
                    "<p style='font-size:12px;color:#6e7681;margin:8px 0 4px'>Perfil dos agentes</p>",
                    unsafe_allow_html=True,
                )
                a1, a2, a3 = st.columns(3)
                with a1:
                    risk = st.slider(
                        "Propensão ao risco", 0.0, 1.0, 0.5, 0.05,
                        key=f"{prefix}risk_{i}",
                        help="Probabilidade base de um agente clicar numa mensagem suspeita.",
                    )
                with a2:
                    awareness = st.slider(
                        "Nível de consciência", 0.0, 1.0, 0.5, 0.05,
                        key=f"{prefix}aware_{i}",
                        help="Literacia em cibersegurança. Valores altos reduzem a taxa de clique.",
                    )
                with a3:
                    hier = st.select_slider(
                        "Nível hierárquico", options=[1, 2, 3], value=1,
                        key=f"{prefix}hier_{i}",
                        help="1 = operacional, 2 = gestão intermédia, 3 = direção.",
                    )

                for j in range(int(n_agents)):
                    dept_agents.append({
                        "name": f"User_{i+1}_{j+1}",
                        "hierarchy_level": hier,
                        "risk_propensity": risk,
                        "awareness_level": awareness,
                    })

            departments.append({"name": name, "agents": dept_agents})

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # ── Guardar preset ────────────────────────────────────────
    _section_card_open("💾  Guardar configuração como preset", "#a371f7")
    _render_save_panel(prefix, departments)
    _section_card_close()

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # ── Secção 2: Ataque ──────────────────────────────────────
    _section_card_open("Ataque", "#f78166")
    ac1, ac2 = st.columns(2)
    with ac1:
        attack_type = st.selectbox(
            "Tipo de ataque", ["Phishing", "Spear Phishing"],
            key=f"{prefix}attack_type",
            help="Phishing: campanha massiva aleatória. Spear Phishing: ataque direcionado aos agentes com hierarquia mais alta.",
        )
    with ac2:
        click_rate = st.slider(
            "Intensidade base do ataque", 0.0, 1.0, 0.5, 0.05,
            key=f"{prefix}click_rate",
            help="Escala a probabilidade de sucesso inicial do atacante antes das defesas serem aplicadas.",
        )
    _section_card_close()

    # ── Secção 3: Defesas ─────────────────────────────────────
    _section_card_open("Defesas", "#3fb950")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.markdown("**MFA**")
        mfa = st.toggle(
            "Ativar MFA", value=True,
            key=f"{prefix}mfa",
            help="Multi-Factor Authentication. Bloqueia ~90% das tentativas de acesso mesmo após credenciais comprometidas.",
        )
    with dc2:
        training = st.slider(
            "Eficácia da formação", 0.0, 1.0, 0.3, 0.05,
            key=f"{prefix}training",
            help="Simula programas de awareness. Aumenta o nível de consciência dos agentes a cada tick.",
        )
    with dc3:
        segmentation = st.slider(
            "Segmentação de rede", 0.0, 1.0, 0.5, 0.05,
            key=f"{prefix}segmentation",
            help="0 = rede plana (lateral movement livre). 1 = zero-trust (propagação entre departamentos bloqueada).",
        )
    _section_card_close()

    return {
        "organization": {"departments": departments},
        "attack":       {"type": attack_type, "click_rate": click_rate},
        "defense":      {"mfa": mfa, "training": training, "segmentation": segmentation},
    }