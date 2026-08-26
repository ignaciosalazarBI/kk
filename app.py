from __future__ import annotations

import html
from urllib.parse import urlencode

import streamlit as st

from design_system import apply_global_style

st.set_page_config(page_title="Control Pyme", page_icon="📊", layout="wide")
apply_global_style()


ICONS = {
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 10.8 12 3l9 7.8"/><path d="M5.5 9.5V21h13V9.5"/><path d="M9.5 21v-6h5v6"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m12 3 1.35 4.15L17.5 8.5l-4.15 1.35L12 14l-1.35-4.15L6.5 8.5l4.15-1.35L12 3Z"/><path d="m18.5 14 .85 2.65L22 17.5l-2.65.85L18.5 21l-.85-2.65L15 17.5l2.65-.85L18.5 14Z"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/></svg>',
    "cash": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9h.01M17 15h.01"/><circle cx="12" cy="12" r="2.2"/></svg>',
    "invoice": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 3h9l3 3v15H6z"/><path d="M14 3v4h4M9 11h6M9 15h6"/></svg>',
    "bank": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m3 9 9-5 9 5"/><path d="M5 10v7M9.5 10v7M14.5 10v7M19 10v7M3 20h18"/></svg>',
    "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m4 7 8-4 8 4-8 4-8-4Z"/><path d="m4 7 8 4v10l-8-4V7ZM20 7l-8 4v10l8-4V7Z"/></svg>',
    "megaphone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 11v2a2 2 0 0 0 2 2h3l8 4V5L8 9H5a2 2 0 0 0-2 2Z"/><path d="m8 15 1.5 5h3"/><path d="M19 9c1 .8 1.5 1.8 1.5 3S20 14.2 19 15"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3 5 6v5c0 4.8 2.8 8.4 7 10 4.2-1.6 7-5.2 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-4"/></svg>',
    "ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9 10h.01M15 10h.01M9 15c1.8 1.2 4.2 1.2 6 0M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>',
    "login": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5"/><path d="m14 8 4 4-4 4M8 12h10"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 18-6-6 6-6"/></svg>',
}


def _preserved_params(extra: dict[str, str]) -> str:
    params = {k: v for k, v in extra.items() if v}
    for key in ("utm_source", "utm_medium", "utm_campaign"):
        value = st.query_params.get(key)
        if value:
            params[key] = str(value)
    return "?" + urlencode(params) if params else "./"


def _module_url(module: str) -> str:
    return _preserved_params({"module": module})


def _public_url(start: str = "") -> str:
    return _preserved_params({"start": start})


def _workspace_url() -> str:
    return _preserved_params({"workspace": "finanzas"})


def _brand() -> None:
    st.sidebar.markdown(
        """
        <div class="cp-brand">
          <div class="cp-brand-mark">CP</div>
          <div>
            <div class="cp-brand-title">Control Pyme</div>
            <div class="cp-brand-sub">Control financiero</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _nav_link(label: str, href: str, icon: str, *, active: bool = False, cta: bool = False, secondary: bool = False) -> None:
    classes = ["cp-nav-link"]
    if active:
        classes.append("active")
    if cta:
        classes.append("cta")
    if secondary:
        classes.append("cp-nav-secondary")
    svg = ICONS.get(icon, ICONS["chart"])
    st.sidebar.markdown(
        f'<a class="{" ".join(classes)}" href="{html.escape(href, quote=True)}">{svg}<span>{html.escape(label)}</span></a>',
        unsafe_allow_html=True,
    )


def _section(label: str, *, secondary: bool = False) -> None:
    extra = " cp-nav-secondary" if secondary else ""
    st.sidebar.markdown(f'<div class="cp-nav-section{extra}">{html.escape(label)}</div>', unsafe_allow_html=True)


def _public_sidebar(start: str = "", module: str = "") -> None:
    _brand()
    _nav_link("Entrar a mi negocio", _workspace_url(), "login", cta=True)

    _section("Principal")
    _nav_link("Inicio", _public_url(), "home", active=not start and not module)
    _nav_link("Diagnóstico", _public_url("diagnostico"), "spark", active=start == "diagnostico")
    _nav_link("Finanzas", _public_url("finanzas"), "chart", active=start == "finanzas")
    _nav_link("Cobranza", _module_url("cobranza"), "cash", active=module == "cobranza")
    _nav_link("Conciliación bancaria", _module_url("conciliacion"), "bank", active=module == "conciliacion")

    _section("Más módulos", secondary=True)
    _nav_link("SII", _module_url("sii"), "invoice", active=module == "sii", secondary=True)
    _nav_link("Inventario", _module_url("inventario"), "box", active=module == "inventario", secondary=True)
    _nav_link("Marketing", _module_url("marketing"), "megaphone", active=module == "marketing", secondary=True)
    _nav_link("Legal", _module_url("legal"), "shield", active=module == "legal", secondary=True)
    _nav_link("Asistente IA", _module_url("ia"), "ai", active=module == "ia", secondary=True)
    _nav_link("Todos los módulos", _public_url("modulos"), "chart", active=start == "modulos", secondary=True)

    st.sidebar.markdown('<div class="cp-sidebar-note">Beta pública · los módulos demo usan datos ficticios.</div>', unsafe_allow_html=True)


def _workspace_sidebar() -> None:
    _brand()
    _section("Mi negocio")
    _nav_link("Resumen financiero", _workspace_url(), "chart", active=True)

    _section("Próximamente", secondary=True)
    st.sidebar.markdown('<div class="cp-soon cp-nav-secondary">Cobranza automática</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cp-soon cp-nav-secondary">Presupuesto y forecast</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="cp-soon cp-nav-secondary">Conciliación bancaria</div>', unsafe_allow_html=True)

    st.sidebar.divider()
    _nav_link("Volver a la demo", _public_url(), "arrow")
    st.sidebar.markdown('<div class="cp-sidebar-note">Tus datos privados están aislados por usuario.</div>', unsafe_allow_html=True)


workspace = str(st.query_params.get("workspace", "")).strip().lower()
module = str(st.query_params.get("module", "")).strip().lower()
start = str(st.query_params.get("start", "")).strip().lower()

if workspace == "finanzas":
    _workspace_sidebar()
    from finance_workspace import render

    render()
elif module:
    _public_sidebar(start, module)
    from beta_runtime import RENDERERS

    renderer = RENDERERS.get(module)
    if renderer is None:
        st.error("Módulo no encontrado.")
        st.markdown("[Volver al inicio](./)")
    else:
        renderer()
else:
    # Render our navigation first. legacy_app still owns the public demo content,
    # but its old sidebar radio is hidden by the design system and controlled by ?start=.
    _public_sidebar(start, "")
    original_set_page_config = st.set_page_config

    def _ignore_second_page_config(*args, **kwargs):
        return None

    st.set_page_config = _ignore_second_page_config
    try:
        import legacy_app  # noqa: F401
    finally:
        st.set_page_config = original_set_page_config
