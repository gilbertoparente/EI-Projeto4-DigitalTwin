import streamlit as st
import time
import pandas as pd
from ui.api_client import step_simulation, get_status


# ── helpers ──────────────────────────────────────────────────────────────────

def _metric_with_tip(col, label: str, value, tip: str, delta=None):
    with col:
        st.metric(label, value, delta=delta, help=tip)


def _ensure_history():
    if "ls_history" not in st.session_state:
        st.session_state.ls_history = []


def _run_steps(n: int, delay: float):
    """Execute n steps sequentially, appending results to session history."""
    _ensure_history()
    progress = st.progress(0, text=f"A executar 0 / {n} steps…")
    for i in range(n):
        data = step_simulation()
        if "error" in data:
            st.error(f"Erro no step {i+1}: {data['error']}")
            break
        entry = data.get("result", {})
        entry["tick"]  = data.get("tick", len(st.session_state.ls_history) + 1)
        entry["total"] = data.get("total_compromised", 0)
        entry["total_agents"] = data.get("total_agents", 1)
        st.session_state.ls_history.append(entry)
        progress.progress((i + 1) / n, text=f"A executar {i+1} / {n} steps…")
        if delay > 0 and i < n - 1:
            time.sleep(delay)
    progress.empty()


# ── main ─────────────────────────────────────────────────────────────────────

def show():
    _ensure_history()

    st.markdown("""
    <h1 style='margin-bottom:.25rem'>📡 Live System</h1>
    <p style='color:#8b949e; font-size:14px; margin-bottom:1.5rem'>
      Execute a simulação passo a passo ou em lote e acompanhe a propagação em tempo real.
    </p>
    """, unsafe_allow_html=True)

    # ── Status bar ────────────────────────────────────────────
    status = get_status()
    offline = "error" in status or status.get("status") == "idle"

    if offline:
        st.warning("⚠️ Simulação não iniciada — vá a **Experiments** e clique em *Inicializar*.")
        return

    total_agents = status.get("agents", 1)
    current_tick = status.get("tick", 0)
    compromised  = status.get("compromised", 0)
    comp_pct     = round(compromised / max(total_agents, 1) * 100, 1)

    m1, m2, m3, m4 = st.columns(4)
    _metric_with_tip(m1, "Agentes totais", total_agents,
                     "Número de CollaboratorAgents criados na organização.")
    _metric_with_tip(m2, "Tick atual", current_tick,
                     "Número de ciclos de simulação executados desde o início.")
    _metric_with_tip(m3, "Comprometidos", compromised,
                     "Agentes cujas credenciais foram capturadas e cujo acesso foi usado pelo atacante.")
    _metric_with_tip(m4, "Taxa de compromisso", f"{comp_pct}%",
                     "Percentagem da população comprometida. KPI principal de exposição da organização.")

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────
    st.markdown("""
    <div style="background:#161b22; border:1px solid #21262d; border-radius:10px;
                padding:1.25rem 1.5rem; margin-bottom:1rem;">
      <div style="font-size:13px; font-weight:600; color:#58a6ff;
                  text-transform:uppercase; letter-spacing:.06em; margin-bottom:.75rem;">
        Execução
      </div>
    """, unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 1])

    with ctrl1:
        if st.button("▶ Step único", use_container_width=True, help="Executa exactamente 1 tick da simulação."):
            _run_steps(1, 0)
            st.rerun()

    with ctrl2:
        n_steps = st.number_input("Nº de steps", min_value=1, max_value=500,
                                  value=10, step=1, label_visibility="collapsed",
                                  key="n_steps_input")

    with ctrl3:
        # Speed selector: maps label → delay between steps
        speed_map = {
            "Máximo": 0.0,
            "Rápido (5/s)": 0.2,
            "Normal (2/s)": 0.5,
            "Lento (1/s)": 1.0,
        }
        speed_label = st.selectbox("Velocidade", list(speed_map.keys()),
                                   index=1, label_visibility="collapsed",
                                   key="speed_select",
                                   help="Intervalo entre steps ao correr em lote.")
        delay = speed_map[speed_label]

    with ctrl4:
        if st.button(f"⏩ Correr {n_steps} steps", use_container_width=True,
                     type="primary",
                     help=f"Executa {n_steps} ticks consecutivos à velocidade selecionada."):
            _run_steps(int(n_steps), delay)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Limpar histórico", help="Apaga o histórico local de métricas (não reinicia a simulação)."):
            st.session_state.ls_history = []
            st.rerun()

    # ── Analytics (integrated) ────────────────────────────────
    if not st.session_state.ls_history:
        st.info("💡 Execute pelo menos um step para ver os gráficos.")
        return

    df = pd.DataFrame(st.session_state.ls_history)
    if "tick" in df.columns:
        df = df.set_index("tick")

    st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px; font-weight:600; color:#c9d1d9;
                text-transform:uppercase; letter-spacing:.06em; margin-bottom:.75rem;">
      📊 Analytics
    </div>
    """, unsafe_allow_html=True)

    chart_cols = st.columns(2)

    # Chart 1: attack funnel per tick
    with chart_cols[0]:
        st.markdown("<p style='font-size:13px; color:#8b949e; margin-bottom:4px'>Funil de ataque por tick</p>",
                    unsafe_allow_html=True)
        funnel_cols = [c for c in ["opened", "clicked", "infected"] if c in df.columns]
        if funnel_cols:
            st.line_chart(df[funnel_cols], height=220)
        else:
            st.caption("Sem dados de funil disponíveis.")

    # Chart 2: cumulative compromise
    with chart_cols[1]:
        st.markdown("<p style='font-size:13px; color:#8b949e; margin-bottom:4px'>Comprometidos acumulados</p>",
                    unsafe_allow_html=True)
        if "total" in df.columns:
            st.area_chart(df["total"], height=220)
        else:
            st.caption("Sem dados de comprometidos disponíveis.")

    # MTTD callout
    if "mttd" in df.columns:
        mttd_val = df["mttd"].dropna()
        if not mttd_val.empty:
            first_detect = int(mttd_val.iloc[0])
            st.info(
                f"🕐 **MTTD (Mean Time to Detect):** primeiro agente comprometido detectado no tick **{first_detect}**.",
                icon=None
            )

    # Summary metrics
    st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
    if "total" in df.columns and not df.empty:
        last = df.iloc[-1]
        s1, s2, s3, s4 = st.columns(4)
        _metric_with_tip(s1, "Comprometidos (último tick)", int(last.get("total", 0)),
                         "Total acumulado de agentes comprometidos no último tick executado.")
        _metric_with_tip(s2, "Infetados neste step",
                         int(last.get("infected", 0)),
                         "Agentes que ficaram comprometidos especificamente no último tick.")
        _metric_with_tip(s3, "Abriram email",
                         int(last.get("opened", 0)),
                         "Agentes que receberam e abriram a mensagem de phishing neste tick.")
        _metric_with_tip(s4, "Clicaram no link",
                         int(last.get("clicked", 0)),
                         "Agentes que clicaram no link malicioso após abrir o email.")

    # Data table + export
    with st.expander("📋 Histórico completo"):
        styled = df.style.background_gradient(
            cmap="Reds",
            subset=[c for c in ["infected", "total"] if c in df.columns]
        )
        st.dataframe(styled, use_container_width=True)
        csv = df.reset_index().to_csv(index=False).encode("utf-8")
        st.download_button("📥 Exportar CSV",
                           data=csv,
                           file_name="cybertwin_report.csv",
                           mime="text/csv")
