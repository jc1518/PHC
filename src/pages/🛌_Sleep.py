"""Sleep coach"""
import streamlit as st

st.set_page_config(page_title="Sleep", page_icon="🛌")
st.sidebar.header("Sleep")
st.sidebar.write(
    """
A good laugh and a long sleep are the best cures in the doctor’s book.
"""
)
st.header("Sleep Coach 🛌", divider=True)
target_column, dashboard_column, recommendation_column = st.columns(3)

with target_column:
    st.subheader("Target")

with dashboard_column:
    st.subheader("Dashboard")

with recommendation_column:
    st.subheader("Recommendation")
