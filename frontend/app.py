import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SHL GenAI Recommender", layout="centered")
st.title("🎯 SHL GenAI Assessment Recommendation")

query = st.text_area("Enter a Job Description or Query")

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Retrieving recommendations..."):
            response = requests.post("http://localhost:8000/recommend", json={"query": query})
            result = response.json()

            st.subheader("🔎 Top Retrieved Assessments")
            df = pd.DataFrame(result["retrieved"])
            st.dataframe(df)

            st.subheader("💡 AI-Generated Recommendation")
            st.markdown(result["generated_answer"])
