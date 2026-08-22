import streamlit as st

# La app principal se mantiene intacta en legacy_app.py.
# Este wrapper añade accesos visibles a los módulos dentro del mismo sidebar.
import legacy_app  # noqa: F401

st.sidebar.divider()
st.sidebar.markdown("### 🧩 Módulos")
st.sidebar.page_link("pages/1_Cobranza.py", label="📞 Cobranza")
st.sidebar.page_link("pages/2_SII.py", label="🧾 SII")
st.sidebar.page_link("pages/3_Marketing.py", label="📣 Marketing")
st.sidebar.page_link("pages/4_Inventario.py", label="📦 Inventario")
st.sidebar.page_link("pages/5_Conciliacion_bancaria.py", label="🏦 Conciliación bancaria")
st.sidebar.page_link("pages/6_Legal.py", label="⚖️ Legal")
st.sidebar.page_link("pages/7_IA.py", label="🤖 IA")
