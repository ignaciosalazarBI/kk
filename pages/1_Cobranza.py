import streamlit as st
from beta_modules import render_cobranza

st.set_page_config(page_title="Control Pyme · Cobranza", page_icon="📞", layout="wide")
render_cobranza()
