import streamlit as st
from beta_runtime import render_marketing

st.set_page_config(page_title="Control Pyme · Marketing", page_icon="📣", layout="wide")
render_marketing()
