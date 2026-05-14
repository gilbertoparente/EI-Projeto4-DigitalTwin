import streamlit as st
import requests
import pandas as pd
import time

st.title("Real-Time Simulation Dashboard")

history = []

placeholder = st.empty()

while True:

    try:

        response = requests.get("http://127.0.0.1:8000/step")

        if response.status_code == 200:

            data = response.json()

            if "result" in data:

                history.append(data["result"])

                df = pd.DataFrame(history)

                with placeholder.container():

                    st.subheader("📈 KPIs em tempo real")

                    st.line_chart(df["infected"])

                    st.line_chart(df["clicked"])

                    st.line_chart(df["opened"])

                    st.dataframe(df.tail())

            else:

                st.error(data)

    except Exception as e:

        st.error(str(e))

    time.sleep(1)