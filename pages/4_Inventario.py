import streamlit as st
from beta_runtime import render_inventario

st.set_page_config(page_title="Control Pyme · Inventario", page_icon="📦", layout="wide")
render_inventario()
