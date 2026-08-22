import streamlit as st
from beta_runtime import render_conciliacion

st.set_page_config(page_title="Control Pyme · Conciliación", page_icon="🏦", layout="wide")
render_conciliacion()
