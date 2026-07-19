import streamlit as st

def render_sidebar():
    st.sidebar.title("Navigation")
    st.sidebar.radio("Section",["Dashboard"])
