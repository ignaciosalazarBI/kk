from __future__ import annotations

import hmac

import pandas as pd
import requests
import streamlit as st

from admin_analytics import (
    MODULE_PAGE_EVENT_SET,
    build_module_table,
    build_source_table,
    daily_activity,
    event_sessions,
    filter_since,
    filter_tracking,
    module_explorers,
    normalize_tracking,
    pct,
    visit_cohort,
)

TRACKING_CUTOFF_UTC = pd.Timestamp("2026-08-20T04:11:29Z")


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


def fmt_date(values: pd.Series) -> pd.Series:
    return values.dt.tz_convert("America/Santiago").dt.strftime("%d-%m-%Y %H:%M")


def _auth() -> None:
    expected = secret("ADMIN_TOKEN")
    if not expected:
        st.error("Falta ADMIN_TOKEN en Secrets.")
        st.stop()

    st.session_state.setdefault("admin_ok", False)
    st.session_state.setdefault("admin_attempts", 0)

    if st.session_state.admin_ok:
        return

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


def _contacts(leads: pd.DataFrame, beta: pd.DataFrame) -> pd.DataFrame:
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
    return contacts


def main() -> None:
    st.set_page_config(page_title="Control Pyme · Panel Beta", page_icon="🔐", layout="wide")
    st.title("🔐 Control Pyme · Panel Beta")
    st.caption("Validación de producto · tráfico · módulos · conversión · canales · feedback")

    _auth()

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

    leads_all, beta_all, feedback_all, eventos_all = [
        normalize_tracking(as_df(data, key))
        for key in ["leads", "beta", "feedback", "eventos"]
    ]

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

    channel_values = (
        sorted(base_events["utm_source"].dropna().astype(str).unique().tolist())
        if not base_events.empty and "utm_source" in base_events.columns
        else []
    )
    channel = st.sidebar.selectbox("Canal", ["Todos"] + channel_values)

    campaign_source = filter_tracking(base_events, channel, "Todas")
    campaign_values = (
        sorted(campaign_source["utm_campaign"].dropna().astype(str).unique().tolist())
        if not campaign_source.empty and "utm_campaign" in campaign_source.columns
        else []
    )
    campaign = st.sidebar.selectbox("Campaña", ["Todas"] + campaign_values)

    if start is not None:
        cutoff_chile = start.tz_convert("America/Santiago").strftime("%d-%m-%Y %H:%M")
        st.sidebar.caption(f"Datos desde: {cutoff_chile} Chile")
    else:
        st.sidebar.warning("El histórico previo al 20-08 contiene eventos que no se registraban correctamente.")
    st.sidebar.caption("El embudo usa solo sesiones con una visita dentro del mismo período/filtro.")

    filtered_events = filter_tracking(base_events, channel, campaign)
    eventos = visit_cohort(filtered_events)
    leads = filter_tracking(base_leads, channel, campaign)
    beta = filter_tracking(base_beta, channel, campaign)
    feedback = filter_tracking(base_feedback, channel, campaign)

    contacts = _contacts(leads, beta)
    unique_contacts = (
        contacts["Email"].fillna("").astype(str).str.lower().replace("", pd.NA).nunique()
        if not contacts.empty
        else 0
    )

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
            f"📏 Cohorte confiable: {visitas} visitas filtradas · {historical_visits} visitas históricas registradas. "
            "Las conversiones solo consideran sesiones que tienen su evento visita dentro del mismo período y filtro."
        )
    else:
        st.caption("⚠️ Estás viendo todo el histórico; úsalo para volumen, no para conversión completa.")

    tabs = st.tabs(["🎯 Resumen", "🧩 Módulos", "📣 Canales", "📈 Embudo", "👥 Contactos", "⭐ Feedback"])

    with tabs[0]:
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
        if visitas < 50:
            st.info("La muestra todavía es pequeña. Observa señales; no elijas el producto definitivo todavía.")

    with tabs[1]:
        st.subheader("Uso real de los módulos")
        module_table = build_module_table(eventos, visitas)
        st.caption(
            "‘Sesiones que entraron’ mide uso real dentro del cohorte. ‘Interés declarado’ viene de selecciones; "
            "‘Votos prioridad’ mide qué módulo eligieron construir primero."
        )
        display_modules = module_table.copy()
        display_modules["% de visitas"] = display_modules["% de visitas"].map(lambda x: f"{x:.1f}%")
        st.dataframe(display_modules, hide_index=True, width="stretch")
        used = module_table.set_index("Módulo")[["Sesiones que entraron"]]
        if used["Sesiones que entraron"].sum() > 0:
            st.bar_chart(used)
        st.subheader("Primer módulo explorado")
        first_view = module_table[["Módulo", "Primer módulo"]].set_index("Módulo")
        if first_view["Primer módulo"].sum() > 0:
            st.bar_chart(first_view)
        else:
            st.info("Todavía no hay suficientes recorridos para identificar un primer módulo.")

    with tabs[2]:
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
        st.caption("El tráfico direct puede incluir pruebas internas/QA; prioriza campañas UTM para decisiones comerciales.")

    with tabs[3]:
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
        st.caption("El recorrido no es estrictamente secuencial, pero todas las etapas pertenecen al mismo cohorte de visitas.")

        st.subheader("Problemas seleccionados")
        pain = eventos.loc[eventos["evento"].astype(str).str.startswith("dolor_", na=False)].copy() if not eventos.empty else pd.DataFrame()
        if pain.empty:
            st.info("Todavía no hay respuestas suficientes.")
        else:
            pain["Problema"] = pain["evento"].str.replace("dolor_", "", regex=False).str.replace("_", " ").str.title()
            pains = pain.groupby("Problema")["session_id"].nunique().sort_values(ascending=False).rename("Personas").to_frame()
            st.caption("Una misma sesión puede seleccionar más de un problema durante la exploración.")
            st.bar_chart(pains)
            st.dataframe(pains.reset_index(), hide_index=True, width="stretch")

    with tabs[4]:
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

    with tabs[5]:
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
                col
                for col in ["created_at", "puntuacion", "utilidad", "parte_util", "comentario", "utm_source", "utm_medium", "utm_campaign"]
                if col in view.columns
            ]
            st.dataframe(view[show], hide_index=True, width="stretch")

    st.divider()
    st.caption(
        "Panel privado · datos vía Edge Function protegida · cohorte confiable desde 20-08-2026 · "
        f"actualizado {pd.Timestamp.now(tz='America/Santiago').strftime('%d-%m-%Y %H:%M')}"
    )
