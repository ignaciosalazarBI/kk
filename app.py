from __future__ import annotations

import json
import re
import uuid

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme Beta", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:3.2rem; padding-bottom:3rem; max-width:1400px}
[data-testid="stSidebar"] {min-width:235px; max-width:235px}
.kpi {border:1px solid #e7e7e7;border-radius:16px;padding:18px;background:white;min-height:118px;box-shadow:0 2px 10px rgba(0,0,0,.035)}
.kpi .label {font-size:.83rem;color:#68707a;margin-bottom:7px}.kpi .value {font-size:1.72rem;font-weight:800}.kpi .sub {font-size:.78rem;color:#7a818a;margin-top:7px}
.hero {padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,#f8fafc,#eef2ff);border:1px solid #e5e7eb;margin-bottom:16px}
.demo-banner {border:1px solid #f59e0b;background:#fffbeb;border-radius:14px;padding:12px 15px;margin:0 0 18px;line-height:1.45;font-size:.94rem}
.module-card {border:1px solid #e5e7eb;border-radius:16px;padding:14px;background:#fff;min-height:100px}
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
        "utm_source": TRACKING["utm_source"],
        "utm_medium": TRACKING["utm_medium"],
        "utm_campaign": TRACKING["utm_campaign"],
    }, timeout=4)


def page_event(name: str) -> None:
    key = f"seen_{name}"
    if not st.session_state.get(key):
        event(f"pantalla_{name}")
        st.session_state[key] = True


def slug(text: str) -> str:
    repl = text.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")
    return re.sub(r"[^a-z0-9]+", "_", repl).strip("_")


if not st.session_state.get("visit_logged"):
    event("visita")
    st.session_state.visit_logged = True

MODULES = ["Finanzas", "Cobranza", "SII", "Marketing", "Legal", "Inventario", "Conciliación bancaria", "IA"]
MODULE_DESCRIPTIONS = {
    "Finanzas": "Caja, P&L, márgenes, presupuesto y forecast.",
    "Cobranza": "Facturas vencidas, aging, prioridades y recordatorios.",
    "SII": "Documentos, alertas y apoyo para ordenar obligaciones tributarias.",
    "Marketing": "Campañas, leads, conversiones, costo por lead y ROI.",
    "Legal": "Contratos, vencimientos, cláusulas y alertas de riesgo.",
    "Inventario": "Stock, rotación, compras, quiebres y exceso de inventario.",
    "Conciliación bancaria": "Importa cartolas CSV/Excel, sugiere coincidencias y detecta diferencias para revisión.",
    "IA": "Una capa transversal que analiza todo y recomienda qué hacer hoy.",
}

TODAY = pd.Timestamp.today().normalize()
ventas = pd.DataFrame([
    {"cliente":"Cliente Andes","total":1_180_000,"vence":TODAY-pd.Timedelta(days=47),"margen":.31},
    {"cliente":"Servicios Norte","total":730_000,"vence":TODAY-pd.Timedelta(days=8),"margen":.54},
    {"cliente":"Comercial Sur","total":590_000,"vence":TODAY+pd.Timedelta(days=5),"margen":.68},
])
KPIS={"ventas":3_100_000,"margen":2_040_000,"margen_pct":.658,"caja":-190_000,"por_cobrar":float(ventas.total.sum())}

menu_options=["🏠 Inicio","💬 Diagnóstico rápido","🚀 Participar en la Beta","🧩 Módulos","💵 Caja","🚨 Alertas","🏦 Conciliación bancaria","📑 Legal","⭐ Feedback Beta","🔒 Privacidad"]
start=st.query_params.get("start","")
default_map={"diagnostico":1,"beta":2,"modulos":3,"conciliacion":6,"feedback":8,"privacidad":9}
menu=st.sidebar.radio("Control Pyme",menu_options,index=default_map.get(start,0))
st.sidebar.caption("🧪 Beta pública · Chile")
st.sidebar.info("Primero queremos entender qué necesita tu negocio. Puedes recorrer la demo sin entregar datos personales.")

page_slug={menu_options[i]:s for i,s in enumerate(["inicio","diagnostico","beta","modulos","caja","alertas","conciliacion","legal","feedback","privacidad"])}[menu]
page_event(page_slug)

st.markdown('<div class="demo-banner"><b>🧪 DEMO PÚBLICA · DATOS FICTICIOS</b><br>Explora libremente. No ingreses claves, datos bancarios, documentos reales ni información sensible.</div>',unsafe_allow_html=True)

if menu=="🏠 Inicio":
    st.markdown('<div class="hero"><h2 style="margin:0">Una plataforma para gestionar y hacer crecer tu negocio</h2><div style="color:#667085;margin-top:6px">Finanzas, Cobranza, SII, Marketing, Legal, Inventario, Conciliación bancaria e IA en una sola visión.</div></div>',unsafe_allow_html=True)
    st.subheader("¿Qué áreas te gustaría controlar desde un solo lugar?")
    st.caption("Marca todas las que te interesen. No necesitas dejar correo.")
    with st.form("module_interest_home"):
        chosen = st.multiselect("Áreas de interés", MODULES, placeholder="Elige una o varias")
        save_modules = st.form_submit_button("Guardar mis intereses", type="primary", width="stretch")
    if save_modules:
        if not chosen:
            st.warning("Elige al menos un área.")
        else:
            for module in chosen:
                event(f"modulo_{slug(module)}")
            event("modulos_interes_guardados")
            st.success("Gracias. Ya sabemos qué áreas te interesan más.")
            st.link_button("Ver cómo funcionaría →", "?start=modulos", width="stretch")

    st.subheader("Vista rápida del negocio")
    c=st.columns(4)
    with c[0]: kpi("Ventas mes",money(KPIS["ventas"]),"Ejemplo")
    with c[1]: kpi("Margen",f'{KPIS["margen_pct"]:.1%}'.replace(".",","),money(KPIS["margen"]))
    with c[2]: kpi("Caja",money(KPIS["caja"]),"Atención")
    with c[3]: kpi("Por cobrar",money(KPIS["por_cobrar"]),"Ficticio")
    st.info("🤖 **IA:** “Tienes $1,91 MM vencidos. Prioriza esos cobros antes de comprometer pagos no críticos.”")
    st.link_button("💬 Hacer diagnóstico rápido", "?start=diagnostico", type="primary", width="stretch")

elif menu=="💬 Diagnóstico rápido":
    st.title("💬 Diagnóstico rápido")
    st.caption("Menos de 1 minuto. El contacto es opcional.")
    options=["Caja y liquidez","Cobranza","SII / impuestos","Marketing y ventas","Saber mi rentabilidad","Inventario","Conciliación bancaria","Contratos/Legal","Orden general del negocio","Otro"]
    with st.form("diag_rapido"):
        dolor=st.selectbox("1. ¿Qué te preocupa más hoy?",options)
        trabajadores=st.selectbox("2. ¿Cuántas personas trabajan en el negocio?",["1","2–5","6–10","11–25","26–50","Más de 50"])
        sistema=st.multiselect("3. ¿Cómo administras hoy?",["Excel","Contador","ERP","Software de facturación","Cuaderno/WhatsApp","Otro"])
        modulos=st.multiselect("4. ¿Qué módulos te interesarían?",MODULES)
        email=st.text_input("Correo (opcional)",max_chars=180)
        consentimiento=st.checkbox("Si ingreso mi correo, acepto que se guarden estas respuestas y me contacten sobre la Beta.")
        enviar=st.form_submit_button("Ver mi diagnóstico",type="primary",width="stretch")
    if enviar:
        if email.strip() and not valid_email(email):
            st.error("Revisa el formato del correo.")
        elif email.strip() and not consentimiento:
            st.error("Marca el consentimiento si deseas dejar tu correo.")
        else:
            event("diagnostico_visto")
            event(f"dolor_{slug(dolor)}")
            for module in modulos:
                event(f"modulo_{slug(module)}")
            st.success("✅ Diagnóstico listo")
            a,b,c=st.columns(3)
            a.metric("Prioridad",dolor)
            b.metric("Tamaño",trabajadores)
            c.metric("Módulos",len(modulos))
            st.info(f"**Tu primer foco debería ser {dolor}.** La idea es conectar la información de tu negocio y convertirla en acciones concretas.")
            if email.strip():
                payload={"nombre":"Visitante Beta","email":clean(email.lower(),180),"telefono":"","empresa":"","rubro":"Otro","trabajadores":trabajadores,"ventas_mensuales":"Prefiero no indicar","herramienta_actual":clean(", ".join(sistema),180),"dolor_principal":dolor,"vende_credito":"A veces","interes_legal":"Sí" if "Legal" in modulos else "Tal vez","disposicion_pago":"Sin preguntar","comentario":clean("Módulos: "+", ".join(modulos),1200),"consentimiento":True,**TRACKING,"origen":"streamlit_beta","estado":"nuevo"}
                ok,_=supabase_insert("leads",payload)
                if ok: event("diagnostico_contacto")
            st.link_button("🚀 Me interesa probar la Beta","?start=beta",type="primary",width="stretch")

elif menu=="🚀 Participar en la Beta":
    st.title("🚀 Participa en la Beta")
    with st.form("beta"):
        nombre=st.text_input("Nombre *",max_chars=120)
        email=st.text_input("Correo *",max_chars=180)
        empresa=st.text_input("Empresa (opcional)",max_chars=180)
        telefono=st.text_input("WhatsApp (opcional)",max_chars=60)
        modulos_beta=st.multiselect("¿Qué módulos te gustaría probar?",MODULES)
        motivo=st.text_area("¿Qué problema te gustaría resolver primero?",max_chars=800)
        consent=st.checkbox("Acepto que se guarden estos datos y me contacten para coordinar la Beta.")
        send=st.form_submit_button("Quiero participar",type="primary",width="stretch")
    if send:
        if len(nombre.strip())<2: st.error("Escribe tu nombre.")
        elif not valid_email(email): st.error("Ingresa un correo válido.")
        elif not consent: st.error("Necesitamos tu consentimiento para registrarte.")
        else:
            ok,msg=supabase_insert("beta_interes",{"nombre":clean(nombre,120),"email":clean(email.lower(),180),"telefono":clean(telefono,60),"empresa":clean(empresa,180),"motivo":clean(motivo+" | Módulos: "+", ".join(modulos_beta),1200),"plan_interes":"Aún no sé","consentimiento":True,"origen":"cta_beta","estado":"nuevo",**TRACKING})
            if ok:
                event("beta_interes")
                for module in modulos_beta:
                    event(f"modulo_{slug(module)}")
                st.success("✅ Listo. Te contactaremos para coordinar la Beta.")
            elif msg=="duplicado": st.info("Ese correo ya está inscrito en la Beta.")
            else: st.error("No pudimos guardar el registro. Intenta nuevamente.")

elif menu=="🧩 Módulos":
    st.title("🧩 La visión completa")
    st.caption("No todos los módulos están construidos aún; esta Beta nos ayuda a decidir el orden correcto.")
    cols=st.columns(2)
    for i,module in enumerate(MODULES):
        with cols[i%2]:
            st.markdown(f'<div class="module-card"><b>{module}</b><br>{MODULE_DESCRIPTIONS[module]}</div>',unsafe_allow_html=True)
    st.info("🤖 La IA será transversal: combinará Finanzas, Cobranza, SII, Marketing, Legal, Inventario y Conciliación bancaria para recomendar acciones concretas.")
    st.link_button("⭐ Decir qué construir primero","?start=feedback",type="primary",width="stretch")

elif menu=="💵 Caja":
    st.title("💵 Caja proyectada")
    st.metric("Caja hoy",money(KPIS["caja"]))
    st.warning("Una empresa puede tener utilidad y aun así quedarse sin caja.")
    st.dataframe(ventas[["cliente","total","vence","margen"]],hide_index=True,width="stretch")

elif menu=="🚨 Alertas":
    st.title("🚨 Alertas y cobranza")
    x=ventas.copy(); x["Días vencido"]=(TODAY-x.vence).dt.days
    st.dataframe(x[["cliente","total","vence","Días vencido","margen"]],hide_index=True,width="stretch")
    st.info("Próxima capa: recordatorios, promesas de pago y mensajes preparados automáticamente.")

elif menu=="🏦 Conciliación bancaria":
    st.title("🏦 Conciliación bancaria automática")
    st.caption("Vista conceptual del MVP. En esta Beta no cargues cartolas reales.")
    a,b,c=st.columns(3)
    a.metric("Movimientos banco","27","Ejemplo ficticio")
    b.metric("Conciliados automáticamente","24","89%")
    c.metric("Requieren revisión","3","$330 mil")
    demo=pd.DataFrame([
        {"Fecha":"18-08-2026","Movimiento":"Abono Cliente Andes","Banco":850000,"Sistema":850000,"Estado":"✅ Conciliado"},
        {"Fecha":"18-08-2026","Movimiento":"Pago Proveedor A","Banco":-320000,"Sistema":-320000,"Estado":"✅ Conciliado"},
        {"Fecha":"19-08-2026","Movimiento":"Transferencia recibida","Banco":330000,"Sistema":0,"Estado":"⚠️ Revisar"},
    ])
    st.dataframe(demo,hide_index=True,width="stretch")
    st.info("MVP propuesto: importar CSV/Excel del banco → sugerir coincidencias por fecha, monto y referencia → confirmar excepciones. La conexión bancaria directa vendría después de validar demanda.")
    st.info("🤖 **IA:** “Detecté un abono de $330 mil sin documento asociado. Revisa si corresponde a una factura pendiente antes de registrarlo.”")
    st.link_button("⭐ ¿Priorizarías este módulo?","?start=feedback",type="primary",width="stretch")

elif menu=="📑 Legal":
    st.title("📑 Legal")
    st.warning("🔒 La carga de documentos reales está DESACTIVADA en esta Beta pública.")
    a,b,c=st.columns(3)
    a.metric("Renovación automática","Sí","Avisar 60 días antes")
    b.metric("Riesgo","Medio","1 cláusula")
    c.metric("Próximo hito","15 oct","Ficticio")

elif menu=="⭐ Feedback Beta":
    st.title("⭐ Feedback de 30 segundos")
    with st.form("feedback"):
        utilidad=st.radio("¿Te serviría una plataforma así en un negocio real?",["Sí","Tal vez","No"],horizontal=True)
        modulos_feedback=st.multiselect("¿Qué módulos te interesan más?",MODULES)
        parte=st.selectbox("¿Cuál construirías primero?",MODULES)
        nota=st.slider("¿Qué nota le pondrías a la idea?",1,5,4)
        comentario=st.text_area("Opcional: ¿qué debería tener sí o sí?",max_chars=800)
        consent=st.checkbox("Acepto que se guarde este feedback anónimo para mejorar la Beta.")
        send=st.form_submit_button("Enviar feedback",type="primary",width="stretch")
    if send:
        if not consent: st.error("Necesitamos tu consentimiento para guardar el feedback.")
        else:
            ok,_=supabase_insert("feedback_beta",{"puntuacion":int(nota),"utilidad":utilidad,"parte_util":parte,"comentario":clean(comentario+" | Interés: "+", ".join(modulos_feedback),1200),"email":"","consentimiento":True,"origen":"feedback_beta",**TRACKING})
            if ok:
                event("feedback_enviado")
                event(f"modulo_prioridad_{slug(parte)}")
                for module in modulos_feedback:
                    event(f"modulo_{slug(module)}")
                st.success("🙌 Gracias. Esto nos ayuda a decidir qué construir primero.")
            else: st.error("No pudimos guardar el feedback. Intenta nuevamente.")

else:
    st.title("🔒 Privacidad de la Beta")
    st.markdown("""
**Qué guardamos:** solo lo que voluntariamente envíes en formularios y eventos anónimos de uso para entender qué módulos interesan más.

**Qué no necesitamos:** claves, datos bancarios, cartolas, RUT personales, contratos reales ni documentos sensibles.

**Conciliación bancaria en esta Beta:** la vista es demostrativa. No cargues cartolas reales todavía.

**Uso:** validar el producto, priorizar módulos y contactarte únicamente cuando hayas dejado un medio de contacto con consentimiento.

**Eliminación:** puedes solicitar que eliminemos tus datos por el mismo canal por el que recibiste la invitación.
""")
    st.info("Puedes recorrer toda la demo sin entregar datos personales.")

st.divider()
st.caption("Beta · Finanzas · Cobranza · SII · Marketing · Legal · Inventario · Conciliación bancaria · IA · 🧪 Datos ficticios")