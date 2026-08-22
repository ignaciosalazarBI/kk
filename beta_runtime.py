from __future__ import annotations

import streamlit as st
import beta_modules as _modules


def _safe_footer() -> None:
    st.divider()
    st.markdown("[🏠 **← Volver a Control Pyme**](./)")
    st.caption("Beta pública · Información ficticia · Funcionalidades sujetas a validación")


# Streamlit 1.62 puede lanzar KeyError('url_pathname') con st.page_link
# bajo esta arquitectura. Sustituimos el footer por navegación web simple.
_modules._footer = _safe_footer

RENDERERS = {
    "cobranza": _modules.render_cobranza,
    "sii": _modules.render_sii,
    "marketing": _modules.render_marketing,
    "inventario": _modules.render_inventario,
    "conciliacion": _modules.render_conciliacion,
    "legal": _modules.render_legal,
    "ia": _modules.render_ia,
}

render_cobranza = _modules.render_cobranza
render_sii = _modules.render_sii
render_marketing = _modules.render_marketing
render_inventario = _modules.render_inventario
render_conciliacion = _modules.render_conciliacion
render_legal = _modules.render_legal
render_ia = _modules.render_ia
