import streamlit as st
import requests
import time

st.title("Digital Twin - Dashboard")

placeholder = st.empty()

while True:

    try:

        response = requests.get("http://127.0.0.1:8000/status")

        if response.status_code == 200:

            data = response.json()

            with placeholder.container():

                st.metric("Agentes", data["agents"])

                st.metric(
                    "Opened",
                    data["state"]["opened"]
                )

                st.metric(
                    "Clicked",
                    data["state"]["clicked"]
                )

                st.metric(
                    "Infected",
                    data["state"]["infected"]
                )

                st.json(data)

    except Exception as e:

        st.error(str(e))

    time.sleep(1)