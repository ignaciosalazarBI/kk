from __future__ import annotations

import hmac
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Control Pyme · Leads Beta", page_icon="🔐", layout="wide")

st.title("🔐 Control Pyme · Leads Beta")
st.caption("Panel privado de validación comercial")


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def fetch_leads() -> tuple[pd.DataFrame | None, str]:
    url = secret("SUPABASE_URL")
    admin_token = secret("ADMIN_TOKEN")
    if not url or not admin_token:
        return None, "Faltan SUPABASE_URL o ADMIN_TOKEN en Streamlit Secrets."

    try:
        r = requests.post(
            f"{url.rstrip('/')}/functions/v1/controlpyme-leads-private",
            headers={
                "x-admin-token": admin_token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={},
            timeout=15,
        )
        if r.status_code != 200:
            return None, f"No se pudo cargar el panel (HTTP {r.status_code})."
        data = r.json()
        df = pd.DataFrame(data)
        if not df.empty and "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        return df, "ok"
    except Exception as exc:
        return None, f"Error de conexión: {exc}"


expected = secret("ADMIN_TOKEN")
if not expected:
    st.error("El panel todavía no tiene ADMIN_TOKEN configurado en Streamlit Secrets.")
    st.stop()

if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False
if "admin_attempts" not in st.session_state:
    st.session_state.admin_attempts = 0

if not st.session_state.admin_ok:
    if st.session_state.admin_attempts >= 5:
        st.error("Demasiados intentos fallidos en esta sesión. Recarga la página para volver a intentar.")
        st.stop()

    with st.form("login_admin"):
        clave = st.text_input("Clave de administrador", type="password")
        entrar = st.form_submit_button("Entrar", type="primary")

    if entrar:
        if hmac.compare_digest(clave, expected):
            st.session_state.admin_ok = True
            st.session_state.admin_attempts = 0
            st.rerun()
        else:
            st.session_state.admin_attempts += 1
            st.error("Clave incorrecta.")
    st.stop()

col_logout, _ = st.columns([1, 5])
with col_logout:
    if st.button("Cerrar sesión"):
        st.session_state.admin_ok = False
        st.rerun()

leads, msg = fetch_leads()
if leads is None:
    st.error(msg)
    st.stop()

if leads.empty:
    st.info("Todavía no hay leads registrados.")
    st.stop()

n = len(leads)
contact_cols = [c for c in ["email", "telefono"] if c in leads.columns]
contactables = leads[contact_cols].fillna("").astype(str) if contact_cols else pd.DataFrame()
contactables_count = (
    contactables.apply(lambda row: any(v.strip() for v in row), axis=1).sum()
    if not contactables.empty else 0
)
legal_count = (
    leads.get("interes_legal", pd.Series(dtype=str))
    .fillna("")
    .astype(str)
    .str.lower()
    .isin(["sí", "si", "true", "tal vez"])
    .sum()
)
would_pay = ~(
    leads.get("disposicion_pago", pd.Series([""] * n))
    .fillna("")
    .astype(str)
    .str.contains("Aún no pagaría", case=False, regex=False)
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Leads Beta", n)
c2.metric("Con contacto", int(contactables_count))
c3.metric("Interés Legal Pyme", int(legal_count))
c4.metric("No descarta pagar", int(would_pay.sum()))

st.subheader("Qué están buscando")
if "dolor_principal" in leads.columns:
    dolor = (
        leads["dolor_principal"]
        .fillna("Sin respuesta")
        .value_counts()
        .rename_axis("Problema")
        .reset_index(name="Leads")
    )
    st.bar_chart(dolor.set_index("Problema"))

c5, c6 = st.columns(2)
with c5:
    st.subheader("Disposición de pago")
    if "disposicion_pago" in leads.columns:
        pago = (
            leads["disposicion_pago"]
            .fillna("Sin respuesta")
            .value_counts()
            .rename_axis("Rango")
            .reset_index(name="Leads")
        )
        st.dataframe(pago, hide_index=True, width="stretch")
with c6:
    st.subheader("Rubros")
    if "rubro" in leads.columns:
        rubros = (
            leads["rubro"]
            .fillna("Sin respuesta")
            .value_counts()
            .rename_axis("Rubro")
            .reset_index(name="Leads")
        )
        st.dataframe(rubros, hide_index=True, width="stretch")

st.subheader("Leads registrados")
show_cols = [c for c in [
    "created_at", "nombre", "empresa", "email", "telefono", "rubro", "trabajadores",
    "ventas_mensuales", "herramienta_actual", "dolor_principal", "vende_credito",
    "interes_legal", "disposicion_pago", "estado"
] if c in leads.columns]
view = leads[show_cols].copy()
if "created_at" in view.columns:
    view["created_at"] = (
        view["created_at"]
        .dt.tz_convert("America/Santiago")
        .dt.strftime("%d-%m-%Y %H:%M")
    )
st.dataframe(view, hide_index=True, width="stretch")

csv = view.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Descargar leads CSV",
    data=csv,
    file_name="control_pyme_leads.csv",
    mime="text/csv",
)

st.caption(
    "Acceso protegido por Streamlit Secrets y una Edge Function privada. "
    "La tabla de leads continúa bloqueada para lectura pública."
)
