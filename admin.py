from __future__ import annotations

import hmac

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme · Panel Beta", page_icon="🔐", layout="wide")

st.title("🔐 Control Pyme · Panel Beta")
st.caption("Validación comercial · contactos · embudo · feedback")


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def private_api(payload: dict) -> tuple[dict | None, str]:
    url = secret("SUPABASE_URL")
    admin_token = secret("ADMIN_TOKEN")
    if not url or not admin_token:
        return None, "Faltan SUPABASE_URL o ADMIN_TOKEN en Streamlit Secrets."
    try:
        r = requests.post(
            f"{url.rstrip('/')}/functions/v1/controlpyme-leads-private",
            headers={"x-admin-token": admin_token, "Content-Type": "application/json", "Accept": "application/json"},
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


def fmt_date(series: pd.Series) -> pd.Series:
    return series.dt.tz_convert("America/Santiago").dt.strftime("%d-%m-%Y %H:%M")


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

c_logout, c_refresh, _ = st.columns([1, 1, 5])
with c_logout:
    if st.button("Cerrar sesión"):
        st.session_state.admin_ok = False
        st.rerun()
with c_refresh:
    if st.button("Actualizar"):
        st.rerun()

data, msg = private_api({"action": "list"})
if data is None:
    st.error(msg)
    st.stop()

leads = as_df(data, "leads")
beta = as_df(data, "beta")
feedback = as_df(data, "feedback")
eventos = as_df(data, "eventos")

contact_frames = []
if not leads.empty:
    contact_frames.append(pd.DataFrame({
        "_id": leads["id"], "_entity": "lead", "Fecha": leads["created_at"], "Origen registro": "Diagnóstico",
        "Nombre": leads.get("nombre", ""), "Empresa": leads.get("empresa", ""), "Email": leads.get("email", ""),
        "WhatsApp": leads.get("telefono", ""), "Rubro": leads.get("rubro", ""), "Necesidad": leads.get("dolor_principal", ""),
        "Plan": "", "Disposición pago": leads.get("disposicion_pago", ""), "Estado": leads.get("estado", "nuevo"),
        "Canal": leads.get("utm_source", "direct"), "Campaña": leads.get("utm_campaign", ""),
    }))
if not beta.empty:
    contact_frames.append(pd.DataFrame({
        "_id": beta["id"], "_entity": "beta", "Fecha": beta["created_at"], "Origen registro": "Interés Beta",
        "Nombre": beta.get("nombre", ""), "Empresa": beta.get("empresa", ""), "Email": beta.get("email", ""),
        "WhatsApp": beta.get("telefono", ""), "Rubro": "", "Necesidad": beta.get("motivo", ""),
        "Plan": beta.get("plan_interes", ""), "Disposición pago": "", "Estado": beta.get("estado", "nuevo"),
        "Canal": beta.get("utm_source", "direct"), "Campaña": beta.get("utm_campaign", ""),
    }))
contacts = pd.concat(contact_frames, ignore_index=True) if contact_frames else pd.DataFrame()
if not contacts.empty:
    contacts = contacts.sort_values("Fecha", ascending=False).reset_index(drop=True)
unique_contacts = contacts["Email"].fillna("").astype(str).str.lower().replace("", pd.NA).nunique() if not contacts.empty else 0

visitas = diagnosticos = intereses = feedback_completo = feedback_rapido = feedback_total = 0
quick_yes = quick_maybe = quick_no = 0
if not eventos.empty:
    visitas = eventos.loc[eventos["evento"] == "visita", "session_id"].nunique()
    diagnosticos = eventos.loc[eventos["evento"] == "diagnostico_completado", "session_id"].nunique()
    intereses = eventos.loc[eventos["evento"] == "beta_interes", "session_id"].nunique()
    feedback_completo = eventos.loc[eventos["evento"] == "feedback_enviado", "session_id"].nunique()
    quick_events = eventos[eventos["evento"].isin(["feedback_rapido_si", "feedback_rapido_tal_vez", "feedback_rapido_no"])]
    feedback_rapido = quick_events["session_id"].nunique()
    quick_yes = quick_events.loc[quick_events["evento"] == "feedback_rapido_si", "session_id"].nunique()
    quick_maybe = quick_events.loc[quick_events["evento"] == "feedback_rapido_tal_vez", "session_id"].nunique()
    quick_no = quick_events.loc[quick_events["evento"] == "feedback_rapido_no", "session_id"].nunique()
    feedback_sessions = eventos[eventos["evento"].isin(["feedback_enviado", "feedback_rapido_si", "feedback_rapido_tal_vez", "feedback_rapido_no"])]
    feedback_total = feedback_sessions["session_id"].nunique()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Visitas medidas", visitas)
m2.metric("Diagnósticos", diagnosticos, f"{(diagnosticos/visitas*100):.0f}% de visitas" if visitas else "—")
m3.metric("Interés Beta", intereses, f"{(intereses/visitas*100):.0f}% de visitas" if visitas else "—")
m4.metric("Feedback total", feedback_total, f"{(feedback_total/visitas*100):.0f}% de visitas" if visitas else "—")
m5.metric("Contactos únicos", unique_contacts)
st.caption("El embudo de visitas se mide desde la activación del tracking. Los registros anteriores siguen visibles en Contactos.")

TAB_EMBUDO, TAB_CONTACTOS, TAB_FEEDBACK = st.tabs(["📈 Embudo", "👥 Contactos", "⭐ Feedback"])

with TAB_EMBUDO:
    st.subheader("Embudo de conversión")
    funnel_df = pd.DataFrame({
        "Etapa": ["Visitas", "Diagnósticos", "Interés Beta", "Feedback"],
        "Personas": [visitas, diagnosticos, intereses, feedback_total],
        "% sobre visitas": [100 if visitas else 0, diagnosticos/visitas*100 if visitas else 0, intereses/visitas*100 if visitas else 0, feedback_total/visitas*100 if visitas else 0],
    })
    st.dataframe(funnel_df.style.format({"% sobre visitas": "{:.1f}%"}), hide_index=True, width="stretch")
    st.bar_chart(funnel_df.set_index("Etapa")[["Personas"]])

    st.subheader("Conversión por canal")
    if eventos.empty:
        st.info("Todavía no hay eventos medidos con el nuevo tracking.")
    else:
        ev = eventos.copy()
        ev["utm_source"] = ev.get("utm_source", "direct").fillna("direct").replace("", "direct")
        ev["evento_grupo"] = ev["evento"].replace({"feedback_rapido_si":"feedback","feedback_rapido_tal_vez":"feedback","feedback_rapido_no":"feedback","feedback_enviado":"feedback"})
        canal = ev.groupby(["utm_source", "evento_grupo"])["session_id"].nunique().unstack(fill_value=0).reset_index().rename(columns={"utm_source":"Canal","visita":"Visitas","diagnostico_completado":"Diagnósticos","beta_interes":"Interés Beta","feedback":"Feedback"})
        for col in ["Visitas","Diagnósticos","Interés Beta","Feedback"]:
            if col not in canal.columns: canal[col]=0
        canal["Conv. diagnóstico"] = canal.apply(lambda r: f"{(r['Diagnósticos']/r['Visitas']*100):.0f}%" if r["Visitas"] else "—", axis=1)
        canal["Conv. Beta"] = canal.apply(lambda r: f"{(r['Interés Beta']/r['Visitas']*100):.0f}%" if r["Visitas"] else "—", axis=1)
        canal["Conv. feedback"] = canal.apply(lambda r: f"{(r['Feedback']/r['Visitas']*100):.0f}%" if r["Visitas"] else "—", axis=1)
        st.dataframe(canal[["Canal","Visitas","Diagnósticos","Interés Beta","Feedback","Conv. diagnóstico","Conv. Beta","Conv. feedback"]], hide_index=True, width="stretch")

with TAB_CONTACTOS:
    st.subheader("Contactos de diagnóstico + interesados Beta")
    if contacts.empty:
        st.info("Todavía no hay contactos.")
    else:
        editor = contacts.copy(); editor["Fecha"] = fmt_date(editor["Fecha"])
        edited = st.data_editor(editor, hide_index=True, width="stretch", disabled=["_id","_entity","Fecha","Origen registro","Nombre","Empresa","Email","WhatsApp","Rubro","Necesidad","Plan","Disposición pago","Canal","Campaña"], column_config={"_id":None,"_entity":None,"Estado":st.column_config.SelectboxColumn("Estado",options=["nuevo","contactado","beta","cliente","descartado"],required=True)}, key="contact_editor")
        if st.button("Guardar cambios de estado", type="primary"):
            changes=errors=0
            for idx in edited.index:
                if str(editor.loc[idx,"Estado"]) != str(edited.loc[idx,"Estado"]):
                    result, err = private_api({"action":"update_state","entity":str(editor.loc[idx,"_entity"]),"id":str(editor.loc[idx,"_id"]),"estado":str(edited.loc[idx,"Estado"])})
                    if result is not None: changes+=1
                    else: errors+=1
            if errors: st.error(f"Se guardaron {changes} cambios y fallaron {errors}.")
            elif changes: st.success(f"✅ {changes} cambio(s) guardado(s)."); st.rerun()
            else: st.info("No había cambios pendientes.")
        export_cols=[c for c in editor.columns if not c.startswith("_")]
        st.download_button("Descargar contactos CSV", data=editor[export_cols].to_csv(index=False).encode("utf-8-sig"), file_name="control_pyme_contactos_beta.csv", mime="text/csv")

with TAB_FEEDBACK:
    st.subheader("Feedback rápido")
    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Respuestas rápidas", feedback_rapido)
    q2.metric("👍 Sí", quick_yes)
    q3.metric("🤔 Tal vez", quick_maybe)
    q4.metric("👎 No", quick_no)
    if feedback_rapido:
        sentiment = pd.DataFrame({"Respuesta":["Sí","Tal vez","No"],"Personas":[quick_yes,quick_maybe,quick_no]}).set_index("Respuesta")
        st.bar_chart(sentiment)

    st.subheader("Feedback completo")
    if feedback.empty:
        st.info("Todavía no hay feedback con el formulario completo.")
    else:
        avg = feedback["puntuacion"].mean() if "puntuacion" in feedback.columns else 0
        yes = (feedback.get("utilidad", pd.Series(dtype=str)) == "Sí").sum()
        f1,f2,f3=st.columns(3)
        f1.metric("Feedback recibidos",len(feedback)); f2.metric("Nota promedio",f"{avg:.1f} / 5"); f3.metric("Dicen que sí les sirve",int(yes))
        if "parte_util" in feedback.columns:
            parts=feedback["parte_util"].fillna("Sin respuesta").value_counts().rename_axis("Parte").reset_index(name="Respuestas")
            st.bar_chart(parts.set_index("Parte"))
        view=feedback.copy()
        if "created_at" in view.columns: view["created_at"]=fmt_date(view["created_at"])
        show=[c for c in ["created_at","puntuacion","utilidad","parte_util","comentario","email","utm_source","utm_campaign"] if c in view.columns]
        st.dataframe(view[show], hide_index=True, width="stretch")

st.divider()
st.caption("Panel privado · datos obtenidos mediante Edge Function protegida · tablas no expuestas a lectura pública")
