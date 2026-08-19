from __future__ import annotations

import json
import re
import uuid

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme Beta", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:3.2rem; padding-bottom:3rem; max-width:1400px}
[data-testid="stSidebar"] {min-width:235px; max-width:235px}
.kpi {border:1px solid #e7e7e7;border-radius:16px;padding:18px;background:white;min-height:118px;box-shadow:0 2px 10px rgba(0,0,0,.035)}
.kpi .label {font-size:.83rem;color:#68707a;margin-bottom:7px}.kpi .value {font-size:1.72rem;font-weight:800}.kpi .sub {font-size:.78rem;color:#7a818a;margin-top:7px}
.action {padding:14px 16px;border-radius:13px;background:#fff7ed;border:1px solid #fed7aa;margin-bottom:9px}
.hero {padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,#f8fafc,#eef2ff);border:1px solid #e5e7eb;margin-bottom:16px}
.cta {padding:22px;border-radius:18px;background:#0f172a;color:white;margin:18px 0}.cta h3 {margin:0 0 8px;color:white}.cta p {margin:0;color:#dbeafe}
.demo-banner {border:1px solid #f59e0b;background:#fffbeb;border-radius:14px;padding:12px 15px;margin:0 0 18px;line-height:1.45;font-size:.94rem}
.quick-card {border:1px solid #dbeafe;background:#f8fbff;border-radius:18px;padding:18px 20px;margin:14px 0}
@media (max-width:768px){.block-container{padding-top:2.8rem;padding-left:1rem;padding-right:1rem}.demo-banner{font-size:.88rem;padding:10px 12px}}
</style>
""", unsafe_allow_html=True)


def money(v: float) -> str:
    sign = "-" if v < 0 else ""
    v = abs(float(v))
    if v >= 1_000_000:
        return f"{sign}${v/1_000_000:.2f} MM".replace(".", ",")
    if v >= 1_000:
        return f"{sign}${v/1_000:.0f} mil"
    return f"{sign}${v:,.0f}".replace(",", ".")


def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def clean(value: str, limit: int) -> str:
    return " ".join(str(value or "").strip().split())[:limit]


def valid_email(value: str) -> bool:
    value = value.strip()
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value)) and len(value) <= 180


if "tracking" not in st.session_state:
    st.session_state.tracking = {
        "utm_source": clean(st.query_params.get("utm_source", "direct"), 80) or "direct",
        "utm_medium": clean(st.query_params.get("utm_medium", "none"), 80) or "none",
        "utm_campaign": clean(st.query_params.get("utm_campaign", "beta_publica"), 120) or "beta_publica",
        "landing_path": clean(str(st.query_params), 250),
    }
if "beta_session_id" not in st.session_state:
    st.session_state.beta_session_id = str(uuid.uuid4())
TRACKING = dict(st.session_state.tracking)


def supabase_insert(table: str, payload: dict, timeout: int = 10) -> tuple[bool, str]:
    url, key = secret("SUPABASE_URL"), secret("SUPABASE_ANON_KEY")
    if not url or not key:
        return False, "Registro temporalmente no disponible."
    try:
        r = requests.post(
            f"{url.rstrip('/')}/rest/v1/{table}",
            headers={"apikey": key, "Content-Type": "application/json", "Prefer": "return=minimal"},
            data=json.dumps(payload, ensure_ascii=False), timeout=timeout,
        )
        if r.status_code in (200, 201, 204): return True, "ok"
        if r.status_code == 409: return False, "duplicado"
        return False, f"HTTP {r.status_code}"
    except Exception:
        return False, "conexion"


def event(name: str) -> None:
    supabase_insert("eventos_beta", {
        "session_id": st.session_state.beta_session_id,
        "evento": clean(name, 100),
        "utm_source": TRACKING["utm_source"], "utm_medium": TRACKING["utm_medium"], "utm_campaign": TRACKING["utm_campaign"],
    }, timeout=4)


def page_event(name: str) -> None:
    key = f"seen_{name}"
    if not st.session_state.get(key):
        event(f"pantalla_{name}")
        st.session_state[key] = True


if not st.session_state.get("visit_logged"):
    event("visita")
    st.session_state.visit_logged = True

TODAY = pd.Timestamp.today().normalize()
ventas = pd.DataFrame([
    {"cliente":"Cliente Andes","total":1_180_000,"vence":TODAY-pd.Timedelta(days=47),"margen":.31},
    {"cliente":"Servicios Norte","total":730_000,"vence":TODAY-pd.Timedelta(days=8),"margen":.54},
    {"cliente":"Comercial Sur","total":590_000,"vence":TODAY+pd.Timedelta(days=5),"margen":.68},
])
pagos = pd.DataFrame([
    {"proveedor":"Proveedor A","total":320_000,"vence":TODAY+pd.Timedelta(days=4)},
    {"proveedor":"Proveedor B","total":180_000,"vence":TODAY+pd.Timedelta(days=12)},
])
KPIS={"ventas":3_100_000,"margen":2_040_000,"margen_pct":.658,"caja":-190_000,"por_cobrar":float(ventas.total.sum()),"costo_ventas":1_060_000}

menu_options=["🏠 Inicio","💬 Diagnóstico rápido","🚀 Participar en la Beta","💵 Caja","🚨 Alertas","📑 Legal Pyme","💳 Planes Beta","⭐ Feedback Beta","🔒 Privacidad"]
start=st.query_params.get("start","")
if st.query_params.get("participar","")=="1": start="beta"
default_map={"diagnostico":1,"beta":2,"feedback":7,"privacidad":8}
menu=st.sidebar.radio("Control Pyme",menu_options,index=default_map.get(start,0))
st.sidebar.caption("🧪 Beta pública · Chile")
st.sidebar.info("¿Primera vez? Parte por **Diagnóstico rápido**. Toma menos de 1 minuto.")

page_slug={menu_options[i]:s for i,s in enumerate(["inicio","diagnostico","beta","caja","alertas","legal","planes","feedback","privacidad"])}[menu]
page_event(page_slug)

st.markdown('<div class="demo-banner"><b>🧪 DEMO PÚBLICA · DATOS FICTICIOS</b><br>Explora libremente. No ingreses claves, datos bancarios, documentos reales ni información sensible.</div>',unsafe_allow_html=True)

if menu=="🏠 Inicio":
    st.markdown('<div class="hero"><h2 style="margin:0">Control Pyme: entiende tu negocio en segundos</h2><div style="color:#667085;margin-top:6px">Caja, cobranza, rentabilidad y alertas en un solo lugar, sin vivir en planillas.</div></div>',unsafe_allow_html=True)
    st.subheader("¿Cuál es hoy el mayor problema de tu Pyme?")
    st.caption("Elige uno. No te pediremos ningún dato para mostrarte cómo lo abordaríamos.")
    pains=[("💵 Caja","Caja y liquidez"),("📞 Cobranza","Cobranza"),("🧾 SII","SII / impuestos"),("📈 Rentabilidad","Saber mi rentabilidad"),("📦 Inventario","Inventario"),("🧩 Otro","Otro")]
    cols=st.columns(3)
    for i,(label,value) in enumerate(pains):
        if cols[i%3].button(label,key=f"pain_{i}",width="stretch"):
            st.session_state.selected_pain=value
            event("dolor_"+re.sub(r"[^a-z0-9]+","_",value.lower().replace("í","i").replace("ó","o")).strip("_"))
    if st.session_state.get("selected_pain"):
        pain=st.session_state.selected_pain
        messages={
            "Caja y liquidez":"te mostraremos caja actual, cobros/pagos próximos y riesgo de quedarte sin liquidez.",
            "Cobranza":"priorizaremos quién te debe, cuánto, desde cuándo y qué cobrar primero.",
            "SII / impuestos":"buscaremos ayudarte a ordenar obligaciones, documentos y alertas tributarias sin reemplazar a tu contador.",
            "Saber mi rentabilidad":"te ayudaremos a entender margen por cliente, producto o servicio para detectar dónde realmente ganas dinero.",
            "Inventario":"te ayudaremos a controlar stock, rotación y compras para reducir quiebres y exceso de inventario.",
            "Otro":"queremos entender qué parte de la administración te consume más tiempo hoy.",
        }
        st.markdown(f'<div class="quick-card"><b>Perfecto. Si tu problema es {pain}:</b><br>{messages[pain]}</div>',unsafe_allow_html=True)
        st.link_button("Quiero mi diagnóstico rápido →","?start=diagnostico",type="primary",width="stretch")

    st.caption("👇 Ejemplo ficticio de cómo se verá el control diario.")
    c=st.columns(5)
    with c[0]: kpi("Ventas mes",money(KPIS["ventas"]),"Ejemplo")
    with c[1]: kpi("Margen",f'{KPIS["margen_pct"]:.1%}'.replace(".",","),money(KPIS["margen"]))
    with c[2]: kpi("Caja",money(KPIS["caja"]),"Atención")
    with c[3]: kpi("Por cobrar",money(KPIS["por_cobrar"]),"Ficticio")
    with c[4]: kpi("Costo ventas",money(KPIS["costo_ventas"]),"Ejemplo")

elif menu=="💬 Diagnóstico rápido":
    st.title("💬 Diagnóstico rápido")
    st.caption("Menos de 1 minuto. Primero entendemos tu problema; el contacto es opcional.")
    pain_default=st.session_state.get("selected_pain","Caja y liquidez")
    options=["Caja y liquidez","Cobranza","SII / impuestos","Saber mi rentabilidad","Costos y gastos","Inventario","Presupuesto/forecast","Contratos/Legal","Orden general del negocio","Otro"]
    with st.form("diag_rapido"):
        dolor=st.selectbox("1. ¿Qué te preocupa más hoy?",options,index=options.index(pain_default) if pain_default in options else 0)
        trabajadores=st.selectbox("2. ¿Cuántas personas trabajan en el negocio?",["1","2–5","6–10","11–25","26–50","Más de 50"])
        sistema=st.multiselect("3. ¿Cómo administras hoy?",["Excel","Contador","ERP","Software de facturación","Cuaderno/WhatsApp","Otro"])
        credito=st.radio("4. ¿Vendes a crédito?",["Sí","No","A veces"],horizontal=True)
        email=st.text_input("Correo (opcional, si quieres recibir novedades)",max_chars=180)
        consentimiento=st.checkbox("Si ingreso mi correo, acepto que Control Pyme guarde estas respuestas y me contacte sobre la Beta.")
        enviar=st.form_submit_button("Ver mi diagnóstico",type="primary",width="stretch")
    if enviar:
        if email.strip() and not valid_email(email):
            st.error("Revisa el formato del correo.")
        elif email.strip() and not consentimiento:
            st.error("Marca el consentimiento si deseas dejar tu correo.")
        else:
            event("diagnostico_visto")
            riesgo="Alto" if dolor in ["Caja y liquidez","Cobranza"] or credito=="Sí" else "Medio"
            st.success("✅ Diagnóstico listo")
            a,b,c=st.columns(3); a.metric("Prioridad",dolor); b.metric("Riesgo de caja",riesgo); c.metric("Administración",", ".join(sistema) or "Sin indicar")
            st.info(f"**Tu primer foco debería ser {dolor}.** Control Pyme buscará convertir tus datos operativos en una lista corta de acciones para hoy.")
            if email.strip():
                payload={"nombre":"Visitante Beta","email":clean(email.lower(),180),"telefono":"","empresa":"","rubro":"Otro","trabajadores":trabajadores,"ventas_mensuales":"Prefiero no indicar","herramienta_actual":clean(", ".join(sistema),180),"dolor_principal":dolor,"vende_credito":credito,"interes_legal":"Tal vez","disposicion_pago":"Sin preguntar","comentario":"Diagnóstico rápido","consentimiento":True,**TRACKING,"origen":"streamlit_beta","estado":"nuevo"}
                ok,_=supabase_insert("leads",payload)
                if ok: event("diagnostico_contacto")
            st.link_button("🚀 Me interesa probar la Beta","?start=beta",type="primary",width="stretch")
            st.link_button("⭐ Dar feedback de 30 segundos","?start=feedback",width="stretch")

elif menu=="🚀 Participar en la Beta":
    st.title("🚀 Participa en Control Pyme Beta")
    st.caption("Déjanos solo lo necesario para contactarte. No hay cobro ni compromiso.")
    with st.form("beta"):
        nombre=st.text_input("Nombre *",max_chars=120); email=st.text_input("Correo *",max_chars=180)
        empresa=st.text_input("Empresa (opcional)",max_chars=180); telefono=st.text_input("WhatsApp (opcional)",max_chars=60)
        motivo=st.text_area("¿Qué problema te gustaría resolver primero?",max_chars=800)
        consent=st.checkbox("Acepto que Control Pyme guarde estos datos y me contacte para coordinar la Beta.")
        send=st.form_submit_button("Quiero participar",type="primary",width="stretch")
    if send:
        if len(nombre.strip())<2: st.error("Escribe tu nombre.")
        elif not valid_email(email): st.error("Ingresa un correo válido.")
        elif not consent: st.error("Necesitamos tu consentimiento para registrarte.")
        else:
            ok,msg=supabase_insert("beta_interes",{"nombre":clean(nombre,120),"email":clean(email.lower(),180),"telefono":clean(telefono,60),"empresa":clean(empresa,180),"motivo":clean(motivo,800),"plan_interes":"Aún no sé","consentimiento":True,"origen":"cta_beta","estado":"nuevo",**TRACKING})
            if ok:
                event("beta_interes"); st.success("✅ Listo. Te contactaremos para coordinar la Beta."); st.link_button("⭐ Cuéntanos qué te pareció","?start=feedback",width="stretch")
            elif msg=="duplicado": st.info("Ese correo ya está inscrito en la Beta.")
            else: st.error("No pudimos guardar el registro. Intenta nuevamente.")

elif menu=="💵 Caja":
    st.title("💵 Caja proyectada"); st.caption("Escenario ficticio de demostración.")
    st.metric("Caja hoy",money(KPIS["caja"])); st.warning("Una Pyme puede tener utilidad y aun así quedarse sin caja.")
    tabla=pd.concat([ventas.assign(Tipo="Cobro",Entidad=ventas.cliente,Monto=ventas.total,Fecha=ventas.vence)[["Fecha","Tipo","Entidad","Monto"]],pagos.assign(Tipo="Pago",Entidad=pagos.proveedor,Monto=-pagos.total,Fecha=pagos.vence)[["Fecha","Tipo","Entidad","Monto"]]]).sort_values("Fecha")
    st.dataframe(tabla,hide_index=True,width="stretch"); st.link_button("⭐ ¿Te serviría? Danos feedback","?start=feedback",width="stretch")

elif menu=="🚨 Alertas":
    st.title("🚨 Alertas y cobranza"); st.caption("Clientes y montos ficticios.")
    x=ventas.copy(); x["Días vencido"]=(TODAY-x.vence).dt.days
    st.dataframe(x[["cliente","total","vence","Días vencido","margen"]],hide_index=True,width="stretch")
    st.info("Próxima capa: recordatorios, promesas de pago y mensajes de cobranza preparados automáticamente.")

elif menu=="📑 Legal Pyme":
    st.title("📑 Legal Pyme"); st.warning("🔒 La carga de documentos reales está DESACTIVADA en esta Beta pública.")
    a,b,c=st.columns(3); a.metric("Renovación automática","Sí","Avisar 60 días antes"); b.metric("Riesgo","Medio","1 cláusula"); c.metric("Próximo hito","15 oct","Ficticio")
    st.info("Será una herramienta preventiva de apoyo; los casos relevantes deberán poder escalarse a un abogado.")

elif menu=="💳 Planes Beta":
    st.title("💳 Planes Beta"); st.caption("Precios de referencia en validación. No hay cobro dentro de esta Beta.")
    c1,c2,c3=st.columns(3)
    with c1: st.subheader("Control"); st.metric("$19.990 + IVA","/ mes"); st.write("Dashboard · Caja · CxC/CxP · Alertas")
    with c2: st.subheader("Control Pro"); st.metric("$39.990 + IVA","/ mes"); st.write("Cobranza · Presupuesto · Forecast · Bancos")
    with c3: st.subheader("Control 360"); st.metric("$69.990 + IVA","/ mes"); st.write("Todo Pro · Legal Pyme · automatización")
    st.link_button("🚀 Quiero participar","?start=beta",type="primary",width="stretch")

elif menu=="⭐ Feedback Beta":
    st.title("⭐ Feedback de 30 segundos")
    st.caption("No necesitas dejar correo.")
    with st.form("feedback"):
        utilidad=st.radio("¿Te serviría Control Pyme en un negocio real?",["Sí","Tal vez","No"],horizontal=True)
        parte=st.selectbox("¿Qué parte te interesa más?",["Caja","Cobranza","SII / impuestos","Rentabilidad","Inventario","Legal Pyme","Otra"])
        nota=st.slider("¿Qué nota le pondrías a la idea?",1,5,4)
        comentario=st.text_area("Opcional: ¿qué debería tener sí o sí?",max_chars=800)
        consent=st.checkbox("Acepto que Control Pyme guarde este feedback anónimo para mejorar la Beta.")
        send=st.form_submit_button("Enviar feedback",type="primary",width="stretch")
    if send:
        if not consent: st.error("Necesitamos tu consentimiento para guardar el feedback.")
        else:
            ok,_=supabase_insert("feedback_beta",{"puntuacion":int(nota),"utilidad":utilidad,"parte_util":parte,"comentario":clean(comentario,800),"email":"","consentimiento":True,"origen":"feedback_beta",**TRACKING})
            if ok: event("feedback_enviado"); st.success("🙌 Gracias. Esto sí nos ayuda a decidir qué construir.")
            else: st.error("No pudimos guardar el feedback. Intenta nuevamente.")

else:
    st.title("🔒 Privacidad de la Beta")
    st.markdown("""
**Qué guardamos:** solo lo que voluntariamente envíes en los formularios, más el canal de origen de la visita para medir la Beta.

**Qué no necesitamos:** claves, datos bancarios, cartolas, RUT personales, contratos reales ni documentos sensibles.

**Uso:** validar Control Pyme, mejorar el producto y contactarte únicamente cuando hayas dejado un medio de contacto con consentimiento.

**Eliminación:** puedes solicitar que eliminemos tus datos por el mismo canal por el que recibiste la invitación.
""")
    st.info("Puedes recorrer toda la demo sin entregar datos personales.")

st.divider(); st.caption("Control Pyme Beta · El control de tu negocio sin vivir en planillas. · 🧪 Datos ficticios")
