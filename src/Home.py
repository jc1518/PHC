"""Home"""
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", page_icon="🏠")

st.sidebar.header("Home")
st.sidebar.write(
    """
Take care of your body. It's the only place you have to live in.
"""
)

st.write("# Personal Health Coach")
st.divider()

st.image(Image.open("data/home.jpg"), width=600)
