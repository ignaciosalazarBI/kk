import streamlit as st
from beta_runtime import render_legal

st.set_page_config(page_title="Control Pyme · Legal", page_icon="⚖️", layout="wide")
render_legal()
