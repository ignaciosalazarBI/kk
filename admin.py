from __future__ import annotations

import hmac

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme · Panel Beta", page_icon="🔐", layout="wide")
st.title("🔐 Control Pyme · Panel Beta")
st.caption("Validación de producto · tráfico · módulos · conversión · canales · feedback")

TRACKING_CUTOFF_UTC = pd.Timestamp("2026-08-20T04:11:29Z")
MODULE_PAGE_EVENTS = {
    "Finanzas": "pantalla_finanzas",
    "Cobranza": "pantalla_cobranza",
    "SII": "pantalla_sii",
    "Marketing": "pantalla_marketing",
    "Inventario": "pantalla_inventario",
    "Conciliación bancaria": "pantalla_conciliacion_bancaria",
    "Legal": "pantalla_legal",
    "IA": "pantalla_ia",
}
MODULE_INTEREST_EVENTS = {
    "Finanzas": "modulo_finanzas",
    "Cobranza": "modulo_cobranza",
    "SII": "modulo_sii",
    "Marketing": "modulo_marketing",
    "Inventario": "modulo_inventario",
    "Conciliación bancaria": "modulo_conciliacion_bancaria",
    "Legal": "modulo_legal",
    "IA": "modulo_ia",
}
MODULE_PRIORITY_EVENTS = {
    module: event.replace("modulo_", "modulo_prioridad_", 1)
    for module, event in MODULE_INTEREST_EVENTS.items()
}
MODULE_EVENT_TO_NAME = {event: module for module, event in MODULE_PAGE_EVENTS.items()}
MODULE_PAGE_EVENT_SET = set(MODULE_PAGE_EVENTS.values())


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def private_api(payload: dict) -> tuple[dict | None, str]:
    url, token = secret("SUPABASE_URL"), secret("ADMIN_TOKEN")
    if not url or not token:
        return None, "Faltan SUPABASE_URL o ADMIN_TOKEN."
    try:
        r = requests.post(
            f"{url.rstrip('/')}/functions/v1/controlpyme-leads-private",
            headers={
                "x-admin-token": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=18,
        )
        if r.status_code != 200:
            return None, f"No se pudo cargar el panel (HTTP {r.status_code})."
        return r.json(), "ok"
    except Exception as exc:
        return None, f"Error de conexión: {exc}"


def as_df(data: dict, key: str) -> pd.DataFrame:
    df = pd.DataFrame(data.get(key, []))
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    return df


def series(df: pd.DataFrame, name: str, default: str = "") -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df), index=df.index, dtype="object")


def normalize_tracking(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    for name, default in [("utm_source", "direct"), ("utm_medium", "none"), ("utm_campaign", "beta_publica")]:
        if name not in out.columns:
            out[name] = default
        out[name] = out[name].fillna(default).astype(str).str.strip().replace("", default)
    return out


def fmt_date(s: pd.Series) -> pd.Series:
    return s.dt.tz_convert("America/Santiago").dt.strftime("%d-%m-%Y %H:%M")


def filter_since(df: pd.DataFrame, start: pd.Timestamp | None) -> pd.DataFrame:
    if df.empty or start is None or "created_at" not in df.columns:
        return df.copy()
    return df.loc[df["created_at"].notna() & (df["created_at"] >= start)].copy()


def filter_tracking(df: pd.DataFrame, channel: str, campaign: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    if channel != "Todos":
        out = out.loc[out["utm_source"] == channel]
    if campaign != "Todas":
        out = out.loc[out["utm_campaign"] == campaign]
    return out.copy()


def event_sessions(events: pd.DataFrame, event_name: str) -> int:
    if events.empty or "evento" not in events.columns or "session_id" not in events.columns:
        return 0
    return int(events.loc[events["evento"] == event_name, "session_id"].nunique())


def module_explorers(events: pd.DataFrame) -> int:
    if events.empty or "evento" not in events.columns or "session_id" not in events.columns:
        return 0
    return int(events.loc[events["evento"].isin(MODULE_PAGE_EVENT_SET), "session_id"].nunique())


def pct(value: int | float, total: int | float) -> str:
    return f"{value / total * 100:.1f}%" if total else "—"


def build_module_table(events: pd.DataFrame, visits: int) -> pd.DataFrame:
    first_counts: dict[str, int] = {}
    if not events.empty and {"evento", "session_id", "created_at"}.issubset(events.columns):
        pages = events.loc[events["evento"].isin(MODULE_PAGE_EVENT_SET)].copy()
        pages = pages.loc[pages["created_at"].notna()].sort_values("created_at")
        if not pages.empty:
            first = pages.drop_duplicates("session_id", keep="first").copy()
            first["Módulo"] = first["evento"].map(MODULE_EVENT_TO_NAME)
            first_counts = first["Módulo"].value_counts().to_dict()

    rows = []
    for module in MODULE_PAGE_EVENTS:
        viewed = event_sessions(events, MODULE_PAGE_EVENTS[module])
        interested = event_sessions(events, MODULE_INTEREST_EVENTS[module])
        prioritized = event_sessions(events, MODULE_PRIORITY_EVENTS[module])
        rows.append(
            {
                "Módulo": module,
                "Sesiones que entraron": viewed,
                "% de visitas": round(viewed / visits * 100, 1) if visits else 0.0,
                "Primer módulo": int(first_counts.get(module, 0)),
                "Interés declarado": interested,
                "Votos prioridad": prioritized,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["Sesiones que entraron", "Votos prioridad", "Interés declarado"],
        ascending=False,
    ).reset_index(drop=True)


def build_source_table(events: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    columns = [label, "Visitas", "Primer clic", "Exploró módulo", "Diagnóstico", "Interés Beta", "Feedback", "% activación", "% módulo", "% Beta"]
    if events.empty or group_col not in events.columns:
        return pd.DataFrame(columns=columns)

    rows = []
    for value, group in events.groupby(group_col, dropna=False):
        visits = event_sessions(group, "visita")
        first = event_sessions(group, "primera_interaccion")
        modules = module_explorers(group)
        diag = event_sessions(group, "diagnostico_visto")
        beta = event_sessions(group, "beta_interes")
        feedback = event_sessions(group, "feedback_enviado")
        rows.append(
            {
                label: str(value or "Sin dato"),
                "Visitas": visits,
                "Primer clic": first,
                "Exploró módulo": modules,
                "Diagnóstico": diag,
                "Interés Beta": beta,
                "Feedback": feedback,
                "% activación": round(first / visits * 100, 1) if visits else 0.0,
                "% módulo": round(modules / visits * 100, 1) if visits else 0.0,
                "% Beta": round(beta / visits * 100, 1) if visits else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values("Visitas", ascending=False).reset_index(drop=True)


def daily_activity(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or not {"created_at", "evento", "session_id"}.issubset(events.columns):
        return pd.DataFrame()
    ev = events.loc[events["created_at"].notna()].copy()
    if ev.empty:
        return pd.DataFrame()
    ev["Fecha"] = ev["created_at"].dt.tz_convert("America/Santiago").dt.date
    visits = ev.loc[ev["evento"] == "visita"].groupby("Fecha")["session_id"].nunique().rename("Visitas")
    modules = ev.loc[ev["evento"].isin(MODULE_PAGE_EVENT_SET)].groupby("Fecha")["session_id"].nunique().rename("Exploró módulo")
    first = ev.loc[ev["evento"] == "primera_interaccion"].groupby("Fecha")["session_id"].nunique().rename("Primer clic")
    return pd.concat([visits, first, modules], axis=1).fillna(0).astype(int).sort_index()


expected = secret("ADMIN_TOKEN")
if not expected:
    st.error("Falta ADMIN_TOKEN en Secrets.")
    st.stop()
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False
if "admin_attempts" not in st.session_state:
    st.session_state.admin_attempts = 0

if not st.session_state.admin_ok:
    if st.session_state.admin_attempts >= 5:
        st.error("Demasiados intentos fallidos. Recarga la página.")
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

c1, c2, _ = st.columns([1, 1, 5])
with c1:
    if st.button("Cerrar sesión"):
        st.session_state.admin_ok = False
        st.rerun()
with c2:
    if st.button("Actualizar"):
        st.rerun()

data, msg = private_api({"action": "list"})
if data is None:
    st.error(msg)
    st.stop()

leads_all, beta_all, feedback_all, eventos_all = [normalize_tracking(as_df(data, k)) for k in ["leads", "beta", "feedback", "eventos"]]

now_utc = pd.Timestamp.now(tz="UTC")
period = st.sidebar.selectbox(
    "Período",
    [
        "Tracking confiable (recomendado)",
        "Últimos 7 días (solo confiable)",
        "Últimos 30 días (solo confiable)",
        "Todo el histórico",
    ],
    index=0,
)
if period == "Tracking confiable (recomendado)":
    start = TRACKING_CUTOFF_UTC
elif period == "Últimos 7 días (solo confiable)":
    start = max(TRACKING_CUTOFF_UTC, now_utc - pd.Timedelta(days=7))
elif period == "Últimos 30 días (solo confiable)":
    start = max(TRACKING_CUTOFF_UTC, now_utc - pd.Timedelta(days=30))
else:
    start = None

base_events = filter_since(eventos_all, start)
base_leads = filter_since(leads_all, start)
base_beta = filter_since(beta_all, start)
base_feedback = filter_since(feedback_all, start)

channel_values = sorted(base_events["utm_source"].dropna().astype(str).unique().tolist()) if not base_events.empty else []
channel = st.sidebar.selectbox("Canal", ["Todos"] + channel_values)

campaign_source = filter_tracking(base_events, channel, "Todas")
campaign_values = sorted(campaign_source["utm_campaign"].dropna().astype(str).unique().tolist()) if not campaign_source.empty else []
campaign = st.sidebar.selectbox("Campaña", ["Todas"] + campaign_values)

st.sidebar.caption("Los filtros afectan tráfico, módulos, contactos y feedback.")
if start is not None:
    cutoff_chile = start.tz_convert("America/Santiago").strftime("%d-%m-%Y %H:%M")
    st.sidebar.caption(f"Datos desde: {cutoff_chile} Chile")
else:
    st.sidebar.warning("El histórico previo al 20-08 contiene eventos que no se registraban correctamente.")

eventos = filter_tracking(base_events, channel, campaign)
leads = filter_tracking(base_leads, channel, campaign)
beta = filter_tracking(base_beta, channel, campaign)
feedback = filter_tracking(base_feedback, channel, campaign)

frames = []
if not leads.empty:
    frames.append(
        pd.DataFrame(
            {
                "_id": series(leads, "id"),
                "_entity": "lead",
                "Fecha": series(leads, "created_at"),
                "Origen": "Diagnóstico",
                "Nombre": series(leads, "nombre"),
                "Empresa": series(leads, "empresa"),
                "Email": series(leads, "email"),
                "Necesidad": series(leads, "dolor_principal"),
                "Estado": series(leads, "estado", "nuevo"),
                "Canal": series(leads, "utm_source", "direct"),
                "Campaña": series(leads, "utm_campaign", "beta_publica"),
            }
        )
    )
if not beta.empty:
    frames.append(
        pd.DataFrame(
            {
                "_id": series(beta, "id"),
                "_entity": "beta",
                "Fecha": series(beta, "created_at"),
                "Origen": "Interés Beta",
                "Nombre": series(beta, "nombre"),
                "Empresa": series(beta, "empresa"),
                "Email": series(beta, "email"),
                "Necesidad": series(beta, "motivo"),
                "Estado": series(beta, "estado", "nuevo"),
                "Canal": series(beta, "utm_source", "direct"),
                "Campaña": series(beta, "utm_campaign", "beta_publica"),
            }
        )
    )
contacts = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
if not contacts.empty:
    contacts = contacts.sort_values("Fecha", ascending=False).reset_index(drop=True)
unique_contacts = contacts["Email"].fillna("").astype(str).str.lower().replace("", pd.NA).nunique() if not contacts.empty else 0

visitas = event_sessions(eventos, "visita")
primeras = event_sessions(eventos, "primera_interaccion")
modulos_visitados = module_explorers(eventos)
diag_vistos = event_sessions(eventos, "diagnostico_visto")
intereses = event_sessions(eventos, "beta_interes")
feedbacks = event_sessions(eventos, "feedback_enviado")

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Visitas", visitas)
m2.metric("Primer clic", primeras, pct(primeras, visitas))
m3.metric("Exploró módulo", modulos_visitados, pct(modulos_visitados, visitas))
m4.metric("Diagnósticos", diag_vistos, pct(diag_vistos, visitas))
m5.metric("Interés Beta", intereses, pct(intereses, visitas))
m6.metric("Contactos", int(unique_contacts))

historical_visits = event_sessions(eventos_all, "visita")
if start is not None:
    st.caption(
        f"📏 Vista confiable: {visitas} visitas en el período filtrado · {historical_visits} visitas históricas registradas. "
        "El histórico anterior al corte no debe usarse para evaluar conversión de eventos nuevos."
    )
else:
    st.caption("⚠️ Estás viendo todo el histórico; parte del tracking antiguo tenía eventos bloqueados y no sirve para medir conversión completa.")

T0, T1, T2, T3, T4, T5 = st.tabs(
    ["🎯 Resumen", "🧩 Módulos", "📣 Canales", "📈 Embudo", "👥 Contactos", "⭐ Feedback"]
)

with T0:
    st.subheader("Actividad en el tiempo")
    daily = daily_activity(eventos)
    if daily.empty:
        st.info("Todavía no hay actividad suficiente para este filtro.")
    else:
        st.line_chart(daily)
        st.dataframe(daily.reset_index(), hide_index=True, width="stretch")

    module_table = build_module_table(eventos, visitas)
    channel_table = build_source_table(eventos, "utm_source", "Canal")

    a, b, c = st.columns(3)
    top_modules = module_table.loc[module_table["Sesiones que entraron"] > 0]
    top_channels = channel_table.loc[channel_table["Visitas"] > 0]
    a.metric("Módulo más visitado", top_modules.iloc[0]["Módulo"] if not top_modules.empty else "—")
    b.metric("Canal con más tráfico", top_channels.iloc[0]["Canal"] if not top_channels.empty else "—")
    b.caption(f"{int(top_channels.iloc[0]['Visitas'])} visitas" if not top_channels.empty else "Sin tráfico")
    c.metric("Feedback enviado", feedbacks, pct(feedbacks, visitas))

    if visitas < 20:
        st.info("La muestra todavía es pequeña. Usa estas señales para observar comportamiento, no para decidir el producto definitivo.")

with T1:
    st.subheader("Uso real de los módulos")
    module_table = build_module_table(eventos, visitas)
    st.caption(
        "‘Sesiones que entraron’ mide uso real. ‘Interés declarado’ viene de selecciones en formularios. "
        "‘Votos prioridad’ mide qué módulo eligieron construir primero."
    )
    display_modules = module_table.copy()
    display_modules["% de visitas"] = display_modules["% de visitas"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_modules, hide_index=True, width="stretch")

    used = module_table.set_index("Módulo")[["Sesiones que entraron"]]
    if used["Sesiones que entraron"].sum() > 0:
        st.bar_chart(used)
    else:
        st.info("Aún no hay entradas a módulos con este filtro.")

    st.subheader("Primer módulo explorado")
    first_view = module_table[["Módulo", "Primer módulo"]].set_index("Módulo")
    if first_view["Primer módulo"].sum() > 0:
        st.bar_chart(first_view)
    else:
        st.info("Todavía no hay suficientes recorridos para identificar un primer módulo.")

with T2:
    st.subheader("Conversión por canal")
    channel_table = build_source_table(eventos, "utm_source", "Canal")
    if channel_table.empty:
        st.info("No hay tráfico para este filtro.")
    else:
        view = channel_table.copy()
        for col in ["% activación", "% módulo", "% Beta"]:
            view[col] = view[col].map(lambda x: f"{x:.1f}%")
        st.dataframe(view, hide_index=True, width="stretch")

    st.subheader("Conversión por campaña")
    campaign_table = build_source_table(eventos, "utm_campaign", "Campaña")
    if campaign_table.empty:
        st.info("No hay campañas identificadas para este filtro.")
    else:
        cview = campaign_table.copy()
        for col in ["% activación", "% módulo", "% Beta"]:
            cview[col] = cview[col].map(lambda x: f"{x:.1f}%")
        st.dataframe(cview, hide_index=True, width="stretch")

    st.caption("El tráfico ‘direct’ puede incluir pruebas internas/QA; compáralo con campañas UTM antes de sacar conclusiones comerciales.")

with T3:
    st.subheader("Embudo de validación")
    funnel = pd.DataFrame(
        {
            "Etapa": ["Visitas", "Primer clic", "Exploró módulo", "Diagnóstico", "Interés Beta", "Feedback"],
            "Personas": [visitas, primeras, modulos_visitados, diag_vistos, intereses, feedbacks],
        }
    )
    funnel["% sobre visitas"] = funnel["Personas"].map(lambda x: x / visitas * 100 if visitas else 0.0)
    st.dataframe(funnel.style.format({"% sobre visitas": "{:.1f}%"}), hide_index=True, width="stretch")
    st.bar_chart(funnel.set_index("Etapa")[["Personas"]])
    st.caption("Este recorrido no es estrictamente secuencial: un usuario puede explorar un módulo o dejar feedback sin completar todas las etapas anteriores.")

    if not eventos.empty:
        st.subheader("Problemas seleccionados")
        pain = eventos.loc[eventos["evento"].astype(str).str.startswith("dolor_", na=False)].copy()
        if pain.empty:
            st.info("Todavía no hay respuestas suficientes.")
        else:
            pain["Problema"] = (
                pain["evento"]
                .str.replace("dolor_", "", regex=False)
                .str.replace("_", " ")
                .str.title()
            )
            pains = pain.groupby("Problema")["session_id"].nunique().sort_values(ascending=False).rename("Personas").to_frame()
            st.caption("Una misma sesión puede seleccionar más de un problema durante la exploración.")
            st.bar_chart(pains)
            st.dataframe(pains.reset_index(), hide_index=True, width="stretch")

with T4:
    st.subheader("Contactos")
    if contacts.empty:
        st.info("Todavía no hay contactos para este filtro.")
    else:
        editor = contacts.copy()
        editor["Fecha"] = fmt_date(editor["Fecha"])
        edited = st.data_editor(
            editor,
            hide_index=True,
            width="stretch",
            disabled=["_id", "_entity", "Fecha", "Origen", "Nombre", "Empresa", "Email", "Necesidad", "Canal", "Campaña"],
            column_config={
                "_id": None,
                "_entity": None,
                "Estado": st.column_config.SelectboxColumn(
                    "Estado",
                    options=["nuevo", "contactado", "beta", "cliente", "descartado"],
                    required=True,
                ),
            },
            key="contact_editor",
        )
        if st.button("Guardar cambios", type="primary"):
            changes = errors = 0
            for idx in edited.index:
                if str(editor.loc[idx, "Estado"]) != str(edited.loc[idx, "Estado"]):
                    result, _ = private_api(
                        {
                            "action": "update_state",
                            "entity": str(editor.loc[idx, "_entity"]),
                            "id": str(editor.loc[idx, "_id"]),
                            "estado": str(edited.loc[idx, "Estado"]),
                        }
                    )
                    if result is not None:
                        changes += 1
                    else:
                        errors += 1
            if errors:
                st.error(f"Guardados {changes}; fallaron {errors}.")
            elif changes:
                st.success(f"✅ {changes} cambio(s) guardado(s).")
                st.rerun()
            else:
                st.info("No había cambios.")

with T5:
    if feedback.empty:
        st.info("Todavía no hay feedback completo para este filtro.")
    else:
        avg = feedback["puntuacion"].mean() if "puntuacion" in feedback.columns else 0
        yes = (series(feedback, "utilidad") == "Sí").sum()
        a, b, c = st.columns(3)
        a.metric("Respuestas", len(feedback))
        b.metric("Nota promedio", f"{avg:.1f}/5")
        c.metric("Sí les sirve", int(yes))
        if "parte_util" in feedback.columns:
            parts = feedback["parte_util"].fillna("Sin respuesta").value_counts().rename_axis("Prioridad").reset_index(name="Respuestas")
            st.bar_chart(parts.set_index("Prioridad"))
        view = feedback.copy()
        if "created_at" in view.columns:
            view["created_at"] = fmt_date(view["created_at"])
        show = [
            c
            for c in ["created_at", "puntuacion", "utilidad", "parte_util", "comentario", "utm_source", "utm_medium", "utm_campaign"]
            if c in view.columns
        ]
        st.dataframe(view[show], hide_index=True, width="stretch")

st.divider()
st.caption(
    "Panel privado · datos vía Edge Function protegida · tracking confiable desde 20-08-2026 · "
    f"actualizado {pd.Timestamp.now(tz='America/Santiago').strftime('%d-%m-%Y %H:%M')}"
)
