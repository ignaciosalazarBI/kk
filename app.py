from __future__ import annotations

from urllib.parse import urlencode

import streamlit as st

from design_system import apply_global_style

st.set_page_config(page_title="Control Pyme", page_icon="📊", layout="wide")
apply_global_style()


def _preserved_params(extra: dict[str, str]) -> str:
    params = dict(extra)
    for key in ("utm_source", "utm_medium", "utm_campaign"):
        value = st.query_params.get(key)
        if value:
            params[key] = str(value)
    return "?" + urlencode(params)


def _module_url(module: str) -> str:
    return _preserved_params({"module": module})


def _workspace_url() -> str:
    return _preserved_params({"workspace": "finanzas"})


def _sidebar_modules() -> None:
    st.sidebar.markdown("<div style='font-size:.74rem;letter-spacing:.14em;font-weight:800;color:#8EA4D8;margin:.25rem 0 .2rem'>CONTROL PYME</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='font-size:1.16rem;font-weight:750;color:#fff;margin-bottom:1rem'>Decide con tus números</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"[💼 **Mi negocio**]({_workspace_url()})")
    st.sidebar.divider()
    st.sidebar.markdown("#### Explorar módulos")
    links = [
        ("📞 Cobranza", "cobranza"),
        ("🧾 SII", "sii"),
        ("📣 Marketing", "marketing"),
        ("📦 Inventario", "inventario"),
        ("🏦 Conciliación", "conciliacion"),
        ("⚖️ Legal", "legal"),
        ("🤖 IA", "ia"),
    ]
    for label, slug in links:
        st.sidebar.markdown(f"[{label}]({_module_url(slug)})")
    st.sidebar.divider()
    st.sidebar.markdown("[⌂ Volver al inicio](./)")
    st.sidebar.caption("Beta · datos demo fuera de Mi negocio")


def _workspace_sidebar() -> None:
    st.sidebar.markdown("<div style='font-size:.74rem;letter-spacing:.14em;font-weight:800;color:#8EA4D8;margin:.25rem 0 .2rem'>CONTROL PYME</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='font-size:1.16rem;font-weight:750;color:#fff;margin-bottom:1rem'>Mi negocio</div>", unsafe_allow_html=True)
    st.sidebar.markdown("**Finanzas**")
    st.sidebar.caption("Más módulos privados vendrán después de validar esta experiencia.")
    st.sidebar.divider()
    st.sidebar.markdown("[← Volver a la demo](./)")


workspace = str(st.query_params.get("workspace", "")).strip().lower()
module = str(st.query_params.get("module", "")).strip().lower()

if workspace == "finanzas":
    from finance_workspace import render

    _workspace_sidebar()
    render()
elif module:
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
