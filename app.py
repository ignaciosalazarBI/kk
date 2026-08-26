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


def _brand() -> None:
    st.sidebar.markdown(
        """
        <div class="hc-brand">
          <div class="hc-brand-mark">CP</div>
          <div>
            <div class="hc-brand-name">Control Pyme</div>
            <div class="hc-brand-sub">GESTIÓN FINANCIERA</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _nav_link(label: str, href: str, *, active: bool = False, primary: bool = False) -> None:
    classes = ["hc-nav-link"]
    if active:
        classes.append("active")
    if primary:
        classes.append("primary")
    dot = "" if primary else '<span class="hc-nav-dot"></span>'
    st.sidebar.markdown(
        f'<a class="{" ".join(classes)}" href="{href}">{dot}<span>{label}</span></a>',
        unsafe_allow_html=True,
    )


def _sidebar_modules(active_module: str = "") -> None:
    _brand()
    _nav_link("Entrar a mi negocio", _workspace_url(), primary=True)
    st.sidebar.markdown('<div class="hc-nav-label">Explorar</div>', unsafe_allow_html=True)
    links = [
        ("Cobranza", "cobranza"),
        ("SII", "sii"),
        ("Marketing", "marketing"),
        ("Inventario", "inventario"),
        ("Conciliación bancaria", "conciliacion"),
        ("Legal", "legal"),
        ("Asistente IA", "ia"),
    ]
    for label, slug in links:
        _nav_link(label, _module_url(slug), active=active_module == slug)
    st.sidebar.markdown('<div class="hc-nav-label">General</div>', unsafe_allow_html=True)
    _nav_link("Inicio", "./")
    st.sidebar.caption("Beta pública · usa datos demo fuera de Mi negocio")


def _workspace_sidebar() -> None:
    _brand()
    st.sidebar.markdown('<div class="hc-nav-label">Mi negocio</div>', unsafe_allow_html=True)
    _nav_link("Resumen financiero", _workspace_url(), active=True)
    st.sidebar.markdown('<div class="hc-nav-label">Próximamente</div>', unsafe_allow_html=True)
    st.sidebar.markdown("<div style='padding:7px 11px;color:#7F96A2;font-size:.82rem'>Cobranza</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='padding:7px 11px;color:#7F96A2;font-size:.82rem'>Conciliación bancaria</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='padding:7px 11px;color:#7F96A2;font-size:.82rem'>Presupuesto y forecast</div>", unsafe_allow_html=True)
    st.sidebar.divider()
    _nav_link("Volver a la demo", "./")
    st.sidebar.caption("Tus datos financieros están separados por usuario")


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
        st.markdown("[Volver al inicio](./)")
    else:
        renderer()
    _sidebar_modules(module)
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
