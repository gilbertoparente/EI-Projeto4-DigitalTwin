import streamlit as st
import pandas as pd
# O IMPORT MUDOU AQUI:
from ui.api_client import step_simulation


def show():
    st.title("📊 Simulation Analytics")
    st.markdown("Acompanhe a evolução do ataque e a eficácia das medidas de mitigação em cada iteração.")

    # Inicializar o histórico na sessão do Streamlit se não existir
    if "history" not in st.session_state:
        st.session_state.history = []

    # Botões de controlo
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("▶️ Run Next Step", use_container_width=True):
            with st.spinner("Simulando propagação..."):
                data = step_simulation()

                if "error" in data:
                    st.error(f"Erro: {data['error']}")
                elif "result" not in data:
                    st.warning("A simulação ainda não foi iniciada. Vá à página de Experiências.")
                else:
                    # Guardamos os dados da iteração atual
                    entry = data["result"]
                    entry["tick"] = data["tick"]
                    # Adicionamos também o total de infetados acumulados na rede
                    entry["total_network_infection"] = data.get("total_compromised", 0)
                    st.session_state.history.append(entry)

    with col_btn2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    # Visualização de Dados
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).set_index("tick")

        # 1. Gráfico de Linhas Consolidado (Funil de Ataque)
        st.subheader("📈 Attack Funnel")
        # Mostra o comportamento do step atual
        st.line_chart(df[["opened", "clicked", "infected"]])

        # 2. Gráfico de Evolução Acumulada
        st.subheader("☣️ Total Network Compromise")
        # Mostra o crescimento total da infecção na rede
        st.area_chart(df["total_network_infection"])

        # 3. Métricas Acumuladas em Tabela
        st.divider()
        st.subheader("📋 Historical Data Logs")

        # Formatação visual para destacar os riscos
        styled_df = df.style.background_gradient(cmap='Reds', subset=['infected', 'total_network_infection'])
        st.dataframe(styled_df, use_container_width=True)

        # 4. Exportar dados
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download CSV Report",
            data=csv,
            file_name='cyber_simulation_report.csv',
            mime='text/csv',
        )
    else:
        st.info("💡 Nenhum dado acumulado. Certifique-se de que iniciou a simulação e execute o primeiro 'Step'.")


if __name__ == "__main__":
    show()