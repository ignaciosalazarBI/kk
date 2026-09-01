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

WORKSPACES = [
    ("finanzas", "Finanzas", "chart"),
    ("cobranza", "Cobranza", "cash"),
    ("conciliacion", "Conciliación", "bank"),
    ("inventario", "Inventario", "box"),
    ("sii", "SII / Impuestos", "invoice"),
    ("marketing", "Marketing", "megaphone"),
    ("legal", "Legal", "shield"),
    ("ia", "Asistente IA", "ai"),
]


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


def _workspace_url(area: str = "finanzas") -> str:
    return _preserved_params({"workspace": area})


def _brand() -> None:
    st.sidebar.markdown(
        """
        <div class="cp-brand">
          <div class="cp-brand-mark" aria-hidden="true">
            <svg viewBox="0 0 28 28" width="22" height="22" fill="none">
              <rect x="4" y="14" width="4" height="8" rx="2" fill="currentColor" opacity=".72"/>
              <rect x="12" y="8" width="4" height="14" rx="2" fill="currentColor" opacity=".88"/>
              <rect x="20" y="4" width="4" height="18" rx="2" fill="currentColor"/>
              <path d="M5 9.5 12.5 5l6 2.6 5.5-4.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <div class="cp-brand-title">Control Pyme</div>
            <div class="cp-brand-sub">Business control</div>
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
    _nav_link("Abrir mi negocio", _workspace_url(), "login", cta=True)

    _section("Descubrir")
    _nav_link("Inicio", _public_url(), "home", active=not start and not module)
    _nav_link("Diagnóstico", _public_url("diagnostico"), "spark", active=start == "diagnostico")
    _nav_link("Vista financiera", _public_url("finanzas"), "chart", active=start == "finanzas")

    _section("Áreas")
    _nav_link("Cobranza", _module_url("cobranza"), "cash", active=module == "cobranza")
    _nav_link("Conciliación", _module_url("conciliacion"), "bank", active=module == "conciliacion")
    _nav_link("Inventario", _module_url("inventario"), "box", active=module == "inventario")

    _section("Más", secondary=True)
    _nav_link("SII / Impuestos", _module_url("sii"), "invoice", active=module == "sii", secondary=True)
    _nav_link("Marketing", _module_url("marketing"), "megaphone", active=module == "marketing", secondary=True)
    _nav_link("Legal", _module_url("legal"), "shield", active=module == "legal", secondary=True)
    _nav_link("Asistente IA", _module_url("ia"), "ai", active=module == "ia", secondary=True)
    _nav_link("Todos los módulos", _public_url("modulos"), "chart", active=start == "modulos", secondary=True)

    st.sidebar.markdown(
        '<div class="cp-sidebar-note"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#6E79FF;margin-right:6px"></span>Beta pública · datos demo</div>',
        unsafe_allow_html=True,
    )


def _switch_workspace(area: str) -> None:
    """Switch private modules without a browser navigation, preserving session_state/auth."""
    for key in ("module", "start"):
        if key in st.query_params:
            del st.query_params[key]
    st.query_params["workspace"] = area
    st.rerun()


def _workspace_nav_button(label: str, area: str, *, active: bool = False) -> None:
    if st.sidebar.button(
        label,
        key=f"workspace_nav_{area}",
        type="primary" if active else "secondary",
        width="stretch",
    ):
        _switch_workspace(area)


def _workspace_sidebar(active_workspace: str) -> None:
    _brand()
    auth = st.session_state.get("finance_auth") or {}
    email = str((auth.get("user") or {}).get("email") or "")

    # Private navigation uses Streamlit buttons instead of HTML anchors. This keeps
    # the same websocket/session when moving between modules, so login state persists.
    st.sidebar.markdown(
        """
        <style>
        [data-testid="stSidebar"] div[class*="st-key-workspace_nav_"]{margin:2px 0!important;}
        [data-testid="stSidebar"] div[class*="st-key-workspace_nav_"] button{
          width:100%!important;min-height:43px!important;justify-content:flex-start!important;text-align:left!important;
          padding:9px 10px!important;border-radius:11px!important;border:1px solid transparent!important;
          background:transparent!important;color:#B9C1D0!important;box-shadow:none!important;
          font-size:.865rem!important;font-weight:570!important;line-height:1.18!important;
          transition:background .16s ease,border-color .16s ease,color .16s ease,transform .16s ease!important;
        }
        [data-testid="stSidebar"] div[class*="st-key-workspace_nav_"] button:hover{
          background:rgba(255,255,255,.055)!important;color:#F8FAFC!important;transform:translateX(1px)!important;
          border-color:transparent!important;box-shadow:none!important;
        }
        [data-testid="stSidebar"] div[class*="st-key-workspace_nav_"] button[kind="primary"]{
          color:#fff!important;font-weight:680!important;
          background:linear-gradient(90deg,rgba(79,93,255,.22),rgba(79,93,255,.10))!important;
          border-color:rgba(121,132,255,.20)!important;box-shadow:inset 3px 0 0 #6E79FF!important;
        }
        [data-testid="stSidebar"] div[class*="st-key-workspace_nav_"] button[kind="primary"]:hover{
          background:linear-gradient(90deg,rgba(79,93,255,.28),rgba(79,93,255,.13))!important;
          border-color:rgba(121,132,255,.24)!important;transform:none!important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _section("Mi negocio")
    for slug, label, _icon in WORKSPACES:
        _workspace_nav_button(label, slug, active=active_workspace == slug)

    st.sidebar.divider()
    _nav_link("Volver a la demo", _public_url(), "arrow")

    if email:
        initial = html.escape(email[:1].upper())
        safe_email = html.escape(email)
        st.sidebar.markdown(
            f"""
            <div style="margin:14px 5px 2px;padding:11px;border:1px solid rgba(255,255,255,.07);border-radius:12px;background:rgba(255,255,255,.025);display:flex;align-items:center;gap:9px">
              <div style="width:29px;height:29px;border-radius:9px;background:rgba(111,123,255,.16);color:#AAB2FF;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:760">{initial}</div>
              <div style="min-width:0"><div style="font-size:.68rem;color:#778297">Sesión activa</div><div style="font-size:.72rem;color:#B7C0CF;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:174px">{safe_email}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown('<div class="cp-sidebar-note">Inicia sesión para trabajar con tus datos reales.</div>', unsafe_allow_html=True)


workspace = str(st.query_params.get("workspace", "")).strip().lower()
module = str(st.query_params.get("module", "")).strip().lower()
start = str(st.query_params.get("start", "")).strip().lower()

if workspace:
    valid_workspaces = {slug for slug, _, _ in WORKSPACES}
    if workspace not in valid_workspaces:
        workspace = "finanzas"
    _workspace_sidebar(workspace)
    if workspace == "finanzas":
        from finance_workspace import render

        render()
    else:
        from workspace_modules import RENDERERS

        renderer = RENDERERS.get(workspace)
        if renderer is None:
            st.error("Módulo privado no disponible.")
        else:
            renderer()
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
    _public_sidebar(start, "")
    original_set_page_config = st.set_page_config

    def _ignore_second_page_config(*args, **kwargs):
        return None

    st.set_page_config = _ignore_second_page_config
    try:
        import legacy_app  # noqa: F401
    finally:
        st.set_page_config = original_set_page_config
