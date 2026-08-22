from __future__ import annotations

from urllib.parse import urlencode

import streamlit as st

st.set_page_config(page_title="Control Pyme Beta", page_icon="📊", layout="wide")


def _module_url(module: str) -> str:
    params = {"module": module}
    for key in ("utm_source", "utm_medium", "utm_campaign"):
        value = st.query_params.get(key)
        if value:
            params[key] = str(value)
    return "?" + urlencode(params)


def _sidebar_modules() -> None:
    st.sidebar.divider()
    st.sidebar.markdown("### 🧩 Módulos")
    links = [
        ("📞 Cobranza", "cobranza"),
        ("🧾 SII", "sii"),
        ("📣 Marketing", "marketing"),
        ("📦 Inventario", "inventario"),
        ("🏦 Conciliación bancaria", "conciliacion"),
        ("⚖️ Legal", "legal"),
        ("🤖 IA", "ia"),
    ]
    for label, slug in links:
        st.sidebar.markdown(f"[{label}]({_module_url(slug)})")
    st.sidebar.markdown("[🏠 Inicio](./)")


module = str(st.query_params.get("module", "")).strip().lower()

if module:
    from beta_runtime import RENDERERS

    renderer = RENDERERS.get(module)
    if renderer is None:
        st.error("Módulo no encontrado.")
        st.markdown("[← Volver al inicio](./)")
    else:
        renderer()
    _sidebar_modules()
else:
    original_set_page_config = st.set_page_config

    def _ignore_second_page_config(*args, **kwargs):
        return None

    st.set_page_config = _ignore_second_page_config
    try:
        import legacy_app  # noqa: F401
    finally:
        st.set_page_config = original_set_page_config
    _sidebar_modules()
