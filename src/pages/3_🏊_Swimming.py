"""Swimming coach"""
import streamlit as st

st.set_page_config(page_title="Swimming", page_icon="🏊")
st.sidebar.header("Swimming")
st.sidebar.write(
    """
The water is your friend, you don't have to fight with water, 
just share the same spirit as the water, and it will help you move.
"""
)
st.header("Swimming 🏊", divider=True)
target_column, dashboard_column, recommendation_column = st.columns(3)

with target_column:
    st.subheader("Target")
    st.write("TODO")

with dashboard_column:
    st.subheader("Dashboard")
    st.write("TODO")

with recommendation_column:
    st.subheader("Recommendation")
    st.write("TODO")
