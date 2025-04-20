import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")

st.title("🔍 SHL Assessment Recommendation System")
st.markdown("Enter a job description or query, and get relevant SHL assessments.")

query = st.text_area("📄 Job Description or Query", height=200)

if st.button("Recommend"):
    if query.strip() == "":
        st.warning("Please enter a query.")
    else:
        with st.spinner("Fetching recommendations..."):
            try:
                response = requests.post(
                    "http://localhost:8000/recommend",  # Change to deployed API URL later
                    json={"query": query}
                )
                if response.status_code == 200:
                    results = response.json()["recommendations"]
                    if results:
                        df = pd.DataFrame(results)
                        st.success("Here are the recommendations:")
                        st.dataframe(df)
                    else:
                        st.info("No relevant assessments found.")
                else:
                    st.error("Something went wrong with the backend request.")
            except Exception as e:
                st.error(f"Failed to connect to the backend: {e}")
