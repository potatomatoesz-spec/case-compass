# Case Compass: Streamlit App for EU Merger Control Decisions

import streamlit as st
import requests
import pandas as pd
from openai import OpenAI
from datetime import datetime

# --- Configuration ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- App Layout ---
st.set_page_config(page_title="Case Compass", layout="wide")
st.title("Case Compass: EU Merger Control Assistant")

st.sidebar.header("Filters")
year_filter = st.sidebar.selectbox("Select Year", ["All"] + list(range(2000, datetime.now().year+1))[::-1])
search_query = st.sidebar.text_input("Search Case Title or Parties")

# --- Load Dataset (Sample or Preloaded CSV) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("https://raw.githubusercontent.com/openstate/case-compass/main/sample_data.csv")
    except:
        df = pd.read_csv("sample_data.csv")  # fallback
    df['Year'] = pd.to_datetime(df['Date'], errors='coerce').dt.year
    return df

df = load_data()

if year_filter != "All":
    df = df[df['Year'] == int(year_filter)]

if search_query:
    df = df[df['Title'].str.contains(search_query, case=False, na=False)]

st.subheader("EU Merger Control Decisions")
st.dataframe(df[['Case Number', 'Title', 'Date', 'Link']].reset_index(drop=True), use_container_width=True)

# --- Ask Legal Question ---
st.subheader("Ask a Legal Question")
user_question = st.text_area("Ask a question based on EU merger decisions:")

if st.button("Get Answer") and user_question:
    # Sample prompt
    prompt = f"""
    You are a legal assistant trained on EU Commission merger control decisions. Answer the question below ONLY using known Commission practices and publicly available merger cases.

    Question: {user_question}

    If applicable, cite relevant decisions by case number or title.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal expert on EU competition law."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        answer = response.choices[0].message.content
        st.markdown("### Answer")
        st.write(answer)
    except Exception as e:
        st.error(f"Error generating answer: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Built for legal research. Data from European Commission open portal. 🚀")
