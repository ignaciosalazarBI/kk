from __future__ import annotations

import hmac
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme · Panel Beta", page_icon="🔐", layout="wide")
st.title("🔐 Control Pyme · Panel Beta")
st.caption("Validación comercial · embudo · módulos · comportamiento · feedback")


def secret(name: str) -> str:
    try: return str(st.secrets.get(name, ""))
    except Exception: return ""


def private_api(payload: dict) -> tuple[dict | None, str]:
    url, token = secret("SUPABASE_URL"), secret("ADMIN_TOKEN")
    if not url or not token: return None, "Faltan SUPABASE_URL o ADMIN_TOKEN."
    try:
        r=requests.post(f"{url.rstrip('/')}/functions/v1/controlpyme-leads-private",headers={"x-admin-token":token,"Content-Type":"application/json","Accept":"application/json"},json=payload,timeout=18)
        if r.status_code!=200: return None,f"No se pudo cargar el panel (HTTP {r.status_code})."
        return r.json(),"ok"
    except Exception as exc: return None,f"Error de conexión: {exc}"


def as_df(data: dict,key: str)->pd.DataFrame:
    df=pd.DataFrame(data.get(key,[]))
    if not df.empty and "created_at" in df.columns: df["created_at"]=pd.to_datetime(df["created_at"],errors="coerce",utc=True)
    return df


def fmt_date(s: pd.Series)->pd.Series:
    return s.dt.tz_convert("America/Santiago").dt.strftime("%d-%m-%Y %H:%M")

expected=secret("ADMIN_TOKEN")
if not expected: st.error("Falta ADMIN_TOKEN en Secrets."); st.stop()
if "admin_ok" not in st.session_state: st.session_state.admin_ok=False
if "admin_attempts" not in st.session_state: st.session_state.admin_attempts=0
if not st.session_state.admin_ok:
    if st.session_state.admin_attempts>=5: st.error("Demasiados intentos fallidos. Recarga la página."); st.stop()
    with st.form("login_admin"):
        clave=st.text_input("Clave de administrador",type="password")
        entrar=st.form_submit_button("Entrar",type="primary")
    if entrar:
        if hmac.compare_digest(clave,expected): st.session_state.admin_ok=True; st.session_state.admin_attempts=0; st.rerun()
        else: st.session_state.admin_attempts+=1; st.error("Clave incorrecta.")
    st.stop()

c1,c2,_=st.columns([1,1,5])
with c1:
    if st.button("Cerrar sesión"): st.session_state.admin_ok=False; st.rerun()
with c2:
    if st.button("Actualizar"): st.rerun()

data,msg=private_api({"action":"list"})
if data is None: st.error(msg); st.stop()
leads,beta,feedback,eventos=[as_df(data,k) for k in ["leads","beta","feedback","eventos"]]

frames=[]
if not leads.empty:
    frames.append(pd.DataFrame({"_id":leads["id"],"_entity":"lead","Fecha":leads["created_at"],"Origen":"Diagnóstico","Nombre":leads.get("nombre",""),"Empresa":leads.get("empresa",""),"Email":leads.get("email",""),"Necesidad":leads.get("dolor_principal",""),"Estado":leads.get("estado","nuevo"),"Canal":leads.get("utm_source","direct")}))
if not beta.empty:
    frames.append(pd.DataFrame({"_id":beta["id"],"_entity":"beta","Fecha":beta["created_at"],"Origen":"Interés Beta","Nombre":beta.get("nombre",""),"Empresa":beta.get("empresa",""),"Email":beta.get("email",""),"Necesidad":beta.get("motivo",""),"Estado":beta.get("estado","nuevo"),"Canal":beta.get("utm_source","direct")}))
contacts=pd.concat(frames,ignore_index=True) if frames else pd.DataFrame()
if not contacts.empty: contacts=contacts.sort_values("Fecha",ascending=False).reset_index(drop=True)
unique_contacts=contacts["Email"].fillna("").astype(str).str.lower().replace("",pd.NA).nunique() if not contacts.empty else 0

visitas=diag_vistos=intereses=feedbacks=0
if not eventos.empty:
    visitas=eventos.loc[eventos.evento=="visita","session_id"].nunique()
    diag_vistos=eventos.loc[eventos.evento=="diagnostico_visto","session_id"].nunique()
    intereses=eventos.loc[eventos.evento=="beta_interes","session_id"].nunique()
    feedbacks=eventos.loc[eventos.evento=="feedback_enviado","session_id"].nunique()

m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Visitas",visitas)
m2.metric("Diagnósticos",diag_vistos,f"{diag_vistos/visitas*100:.0f}%" if visitas else "—")
m3.metric("Interés Beta",intereses,f"{intereses/visitas*100:.0f}%" if visitas else "—")
m4.metric("Feedback",feedbacks,f"{feedbacks/visitas*100:.0f}%" if visitas else "—")
m5.metric("Contactos",unique_contacts)

T1,T2,T3,T4,T5=st.tabs(["📈 Embudo","🧩 Módulos","🧭 Comportamiento","👥 Contactos","⭐ Feedback"])

with T1:
    funnel=pd.DataFrame({"Etapa":["Visitas","Diagnóstico","Interés Beta","Feedback"],"Personas":[visitas,diag_vistos,intereses,feedbacks]})
    funnel["% sobre visitas"]=[100 if visitas else 0]+[(x/visitas*100 if visitas else 0) for x in [diag_vistos,intereses,feedbacks]]
    st.dataframe(funnel.style.format({"% sobre visitas":"{:.1f}%"}),hide_index=True,width="stretch")
    st.bar_chart(funnel.set_index("Etapa")[["Personas"]])
    if not eventos.empty:
        ev=eventos.copy(); ev["utm_source"]=ev.get("utm_source","direct").fillna("direct").replace("","direct")
        canal=ev.groupby(["utm_source","evento"])["session_id"].nunique().unstack(fill_value=0)
        out=pd.DataFrame({"Canal":canal.index,"Visitas":canal.get("visita",0),"Diagnóstico":canal.get("diagnostico_visto",0),"Interés Beta":canal.get("beta_interes",0),"Feedback":canal.get("feedback_enviado",0)}).reset_index(drop=True)
        st.subheader("Conversión por canal"); st.dataframe(out,hide_index=True,width="stretch")

with T2:
    st.subheader("Interés por módulo")
    if eventos.empty:
        st.info("Todavía no hay eventos.")
    else:
        mod=eventos[eventos.evento.str.startswith("modulo_",na=False) & ~eventos.evento.str.startswith("modulo_prioridad_",na=False) & (eventos.evento!="modulos_interes_guardados")].copy()
        if mod.empty: st.info("Todavía no hay selecciones de módulos con la nueva versión.")
        else:
            mod["Módulo"]=mod.evento.str.replace("modulo_","",regex=False).str.replace("_"," ").str.title().replace({"Sii":"SII","Ia":"IA"})
            table=mod.groupby("Módulo")["session_id"].nunique().sort_values(ascending=False).rename("Personas").to_frame()
            st.bar_chart(table); st.dataframe(table.reset_index(),hide_index=True,width="stretch")

        st.subheader("Módulo que construirían primero")
        pri=eventos[eventos.evento.str.startswith("modulo_prioridad_",na=False)].copy()
        if pri.empty: st.info("Aún no hay prioridades explícitas.")
        else:
            pri["Módulo"]=pri.evento.str.replace("modulo_prioridad_","",regex=False).str.replace("_"," ").str.title().replace({"Sii":"SII","Ia":"IA"})
            ptable=pri.groupby("Módulo")["session_id"].nunique().sort_values(ascending=False).rename("Votos").to_frame()
            st.bar_chart(ptable); st.dataframe(ptable.reset_index(),hide_index=True,width="stretch")

with T3:
    st.subheader("Pantallas visitadas")
    if eventos.empty: st.info("Todavía no hay eventos.")
    else:
        screen=eventos[eventos.evento.str.startswith("pantalla_",na=False)].copy()
        if screen.empty: st.info("Aún no hay suficiente tráfico con tracking por pantalla.")
        else:
            screen["Pantalla"]=screen.evento.str.replace("pantalla_","",regex=False).str.replace("_"," ").str.title()
            screens=screen.groupby("Pantalla")["session_id"].nunique().sort_values(ascending=False).rename("Sesiones").to_frame()
            st.bar_chart(screens); st.dataframe(screens.reset_index(),hide_index=True,width="stretch")
        st.subheader("Problema principal")
        pain=eventos[eventos.evento.str.startswith("dolor_",na=False)].copy()
        if pain.empty: st.info("Todavía no hay respuestas suficientes.")
        else:
            pain["Problema"]=pain.evento.str.replace("dolor_","",regex=False).str.replace("_"," ").str.title()
            pains=pain.groupby("Problema")["session_id"].nunique().sort_values(ascending=False).rename("Personas").to_frame()
            st.bar_chart(pains); st.dataframe(pains.reset_index(),hide_index=True,width="stretch")

with T4:
    st.subheader("Contactos")
    if contacts.empty: st.info("Todavía no hay contactos.")
    else:
        editor=contacts.copy(); editor["Fecha"]=fmt_date(editor["Fecha"])
        edited=st.data_editor(editor,hide_index=True,width="stretch",disabled=["_id","_entity","Fecha","Origen","Nombre","Empresa","Email","Necesidad","Canal"],column_config={"_id":None,"_entity":None,"Estado":st.column_config.SelectboxColumn("Estado",options=["nuevo","contactado","beta","cliente","descartado"],required=True)},key="contact_editor")
        if st.button("Guardar cambios",type="primary"):
            changes=errors=0
            for idx in edited.index:
                if str(editor.loc[idx,"Estado"])!=str(edited.loc[idx,"Estado"]):
                    result,_=private_api({"action":"update_state","entity":str(editor.loc[idx,"_entity"]),"id":str(editor.loc[idx,"_id"]),"estado":str(edited.loc[idx,"Estado"])})
                    if result is not None: changes+=1
                    else: errors+=1
            if errors: st.error(f"Guardados {changes}; fallaron {errors}.")
            elif changes: st.success(f"✅ {changes} cambio(s) guardado(s)."); st.rerun()
            else: st.info("No había cambios.")

with T5:
    if feedback.empty: st.info("Todavía no hay feedback completo.")
    else:
        avg=feedback.puntuacion.mean() if "puntuacion" in feedback.columns else 0
        yes=(feedback.get("utilidad",pd.Series(dtype=str))=="Sí").sum()
        a,b,c=st.columns(3); a.metric("Respuestas",len(feedback)); b.metric("Nota promedio",f"{avg:.1f}/5"); c.metric("Sí les sirve",int(yes))
        if "parte_util" in feedback.columns:
            parts=feedback.parte_util.fillna("Sin respuesta").value_counts().rename_axis("Prioridad").reset_index(name="Respuestas")
            st.bar_chart(parts.set_index("Prioridad"))
        view=feedback.copy()
        if "created_at" in view.columns: view["created_at"]=fmt_date(view["created_at"])
        show=[c for c in ["created_at","puntuacion","utilidad","parte_util","comentario","utm_source","utm_campaign"] if c in view.columns]
        st.dataframe(view[show],hide_index=True,width="stretch")

st.divider(); st.caption("Panel privado · datos vía Edge Function protegida")
