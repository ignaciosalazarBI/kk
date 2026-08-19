from __future__ import annotations

import json
import re
import uuid

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Control Pyme Beta", page_icon="📊", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top:3.4rem; padding-bottom:3rem; max-width:1400px}
[data-testid="stSidebar"] {min-width:235px; max-width:235px}
.kpi {border:1px solid #e7e7e7;border-radius:16px;padding:18px;background:white;min-height:118px;box-shadow:0 2px 10px rgba(0,0,0,.035)}
.kpi .label {font-size:.83rem;color:#68707a;margin-bottom:7px}
.kpi .value {font-size:1.72rem;font-weight:800;line-height:1.05}
.kpi .sub {font-size:.78rem;color:#7a818a;margin-top:7px}
.action {padding:14px 16px;border-radius:13px;background:#fff7ed;border:1px solid #fed7aa;margin-bottom:9px}
.hero {padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,#f8fafc,#eef2ff);border:1px solid #e5e7eb;margin-bottom:16px}
.cta {padding:22px;border-radius:18px;background:#0f172a;color:white;margin:18px 0}
.cta h3 {margin:0 0 8px 0;color:white}
.cta p {margin:0;color:#dbeafe}
.step {border:1px solid #e5e7eb;border-radius:16px;padding:16px;min-height:138px;background:#fff}
.step b {font-size:1.02rem}
.demo-banner {border:1px solid #f59e0b;background:#fffbeb;border-radius:14px;padding:12px 15px;margin:0 0 18px 0;line-height:1.45;font-size:.94rem}
.quick-feedback {border:1px solid #dbeafe;background:#f8fbff;border-radius:16px;padding:16px 18px;margin-top:20px}
@media (max-width: 768px) {
  .block-container {padding-top:3rem; padding-left:1rem; padding-right:1rem}
  .demo-banner {font-size:.88rem;padding:10px 12px}
}
</style>
""",
    unsafe_allow_html=True,
)


def money(v: float) -> str:
    sign = "-" if v < 0 else ""
    v = abs(float(v))
    if v >= 1_000_000:
        return f"{sign}${v / 1_000_000:.2f} MM".replace(".", ",")
    if v >= 1_000:
        return f"{sign}${v / 1_000:.0f} mil"
    return f"{sign}${v:,.0f}".replace(",", ".")


def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def get_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def valid_email(value: str) -> bool:
    value = value.strip()
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value)) and len(value) <= 180


def clean(value: str, limit: int) -> str:
    return " ".join(str(value or "").strip().split())[:limit]


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


def supabase_insert(table: str, payload: dict, timeout: int = 12) -> tuple[bool, str]:
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_ANON_KEY")
    if not url or not key:
        return False, "El registro de la Beta no está disponible temporalmente."
    try:
        r = requests.post(
            f"{url.rstrip('/')}/rest/v1/{table}",
            headers={"apikey": key, "Content-Type": "application/json", "Prefer": "return=minimal"},
            data=json.dumps(payload, ensure_ascii=False),
            timeout=timeout,
        )
        if r.status_code in (200, 201, 204):
            return True, "Registro guardado."
        if r.status_code == 409:
            return False, "Ya existe un registro con ese correo."
        if r.status_code == 429:
            return False, "Hubo demasiados intentos. Espera unos minutos y vuelve a probar."
        return False, f"No pudimos guardar el registro (HTTP {r.status_code})."
    except Exception:
        return False, "No pudimos conectar con el registro de la Beta. Intenta nuevamente."


def funnel_event(evento: str) -> None:
    payload = {
        "session_id": st.session_state.beta_session_id,
        "evento": evento,
        "utm_source": TRACKING["utm_source"],
        "utm_medium": TRACKING["utm_medium"],
        "utm_campaign": TRACKING["utm_campaign"],
    }
    supabase_insert("eventos_beta", payload, timeout=4)


if not st.session_state.get("visit_logged", False):
    funnel_event("visita")
    st.session_state.visit_logged = True


def save_lead(payload: dict) -> tuple[bool, str]:
    return supabase_insert("leads", {**payload, **TRACKING, "origen": "streamlit_beta", "estado": "nuevo"})


def save_beta_interest(payload: dict) -> tuple[bool, str]:
    return supabase_insert("beta_interes", {**payload, **TRACKING, "origen": "cta_beta", "estado": "nuevo"})


def save_feedback(payload: dict) -> tuple[bool, str]:
    return supabase_insert("feedback_beta", {**payload, **TRACKING, "origen": "feedback_beta"})


def activate_quick_feedback(context: str) -> None:
    st.session_state.quick_feedback_context = context
    st.session_state.quick_feedback_done = False


TODAY = pd.Timestamp.today().normalize()
ventas = pd.DataFrame([
    {"cliente": "Cliente Andes", "total": 1_180_000, "vence": TODAY - pd.Timedelta(days=47), "margen": 0.31},
    {"cliente": "Servicios Norte", "total": 730_000, "vence": TODAY - pd.Timedelta(days=8), "margen": 0.54},
    {"cliente": "Comercial Sur", "total": 590_000, "vence": TODAY + pd.Timedelta(days=5), "margen": 0.68},
])
pagos = pd.DataFrame([
    {"proveedor": "Proveedor A", "total": 320_000, "vence": TODAY + pd.Timedelta(days=4)},
    {"proveedor": "Proveedor B", "total": 180_000, "vence": TODAY + pd.Timedelta(days=12)},
])
KPIS = {"ventas": 3_100_000, "margen": 2_040_000, "margen_pct": 0.658, "caja": -190_000, "por_cobrar": float(ventas.total.sum()), "costo_ventas": 1_060_000}

menu_options = ["🏠 Inicio", "💬 Diagnóstico Pyme", "🚀 Participar en la Beta", "💵 Caja", "🚨 Alertas", "📑 Legal Pyme", "💳 Planes Beta", "⭐ Feedback Beta", "🔒 Privacidad"]
start = st.query_params.get("start", "")
if st.query_params.get("participar", "") == "1":
    start = "beta"
default_map = {"diagnostico": 1, "beta": 2, "feedback": 7, "privacidad": 8}
menu = st.sidebar.radio("Control Pyme", menu_options, index=default_map.get(start, 0))
st.sidebar.caption("🧪 Beta pública · Chile")
st.sidebar.info("¿Primera vez? Parte por **Diagnóstico Pyme**. No necesitas conectar bancos ni subir documentos.")

st.markdown('<div class="demo-banner"><b>🧪 DEMO PÚBLICA · DATOS FICTICIOS</b><br>Explora libremente. No ingreses claves, datos bancarios, documentos reales ni información sensible.</div>', unsafe_allow_html=True)

if menu == "🏠 Inicio":
    st.markdown('<div class="hero"><h2 style="margin:0">Control Pyme: entiende tu negocio en segundos</h2><div style="color:#667085;margin-top:6px">Caja, cobranza, rentabilidad y alertas en un solo lugar, sin vivir en planillas.</div></div>', unsafe_allow_html=True)
    st.subheader("Empieza aquí")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<div class="step"><b>1️⃣ Haz tu diagnóstico</b><br><br>Cuéntanos cómo administras tu Pyme. Toma cerca de 2 minutos.</div>', unsafe_allow_html=True)
        st.link_button("Hacer diagnóstico", "?start=diagnostico", type="primary", width="stretch")
    with s2:
        st.markdown('<div class="step"><b>2️⃣ Explora la demo</b><br><br>Mira cómo Control Pyme detectaría problemas de caja, cobranza y margen.</div>', unsafe_allow_html=True)
        st.caption("Puedes navegar por Caja, Alertas, Legal y Planes desde el menú.")
    with s3:
        st.markdown('<div class="step"><b>3️⃣ Danos tu opinión</b><br><br>Dinos si te serviría, qué faltó y qué construirías primero.</div>', unsafe_allow_html=True)
        st.link_button("Dar feedback", "?start=feedback", width="stretch")

    st.caption("👇 Lo que sigue es un negocio ficticio de ejemplo para que puedas probar la experiencia.")
    cols = st.columns(5)
    with cols[0]: kpi("Ventas mes", money(KPIS["ventas"]), "Ejemplo neto")
    with cols[1]: kpi("Margen bruto", f'{KPIS["margen_pct"]:.1%}'.replace(".", ","), money(KPIS["margen"]))
    with cols[2]: kpi("Caja disponible", money(KPIS["caja"]), "Ejemplo crítico")
    with cols[3]: kpi("Por cobrar", money(KPIS["por_cobrar"]), "3 documentos ficticios")
    with cols[4]: kpi("Costo ventas", money(KPIS["costo_ventas"]), "Mes ficticio")

    st.subheader("🚨 Requiere acción")
    vencido = ventas[ventas.vence < TODAY]
    st.markdown(f'<div class="action"><b>Caja bajo mínimo.</b> Tienes {money(vencido.total.sum())} vencidos. Prioriza cobranza antes de pagos no críticos.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="action"><b>{len(vencido)} clientes con documentos vencidos.</b> El más antiguo lleva {(TODAY - vencido.vence.min()).days} días.</div>', unsafe_allow_html=True)
    bajo = ventas[ventas.margen < 0.35]
    if not bajo.empty:
        st.markdown(f'<div class="action"><b>Margen bajo.</b> Revisa {bajo.iloc[0].cliente}: margen estimado {bajo.iloc[0].margen:.0%}.</div>', unsafe_allow_html=True)

    st.subheader("Próximos 30 días")
    cobros_30 = ventas[(ventas.vence >= TODAY) & (ventas.vence <= TODAY + pd.Timedelta(days=30))].total.sum() + vencido.total.sum()
    pagos_30 = pagos[pagos.vence <= TODAY + pd.Timedelta(days=30)].total.sum()
    caja_30 = KPIS["caja"] + cobros_30 - pagos_30
    a, b, c = st.columns(3)
    with a: kpi("Cobros esperados", money(cobros_30), "Incluye vencidos ficticios")
    with b: kpi("Pagos esperados", money(pagos_30), "30 días")
    with c: kpi("Caja proyectada 30d", money(caja_30), "Escenario de ejemplo")

    movs, saldo = [], KPIS["caja"]
    movimientos = pd.concat([
        ventas.assign(tipo="Cobro", monto=ventas.total, fecha=ventas.vence)[["fecha", "tipo", "monto"]],
        pagos.assign(tipo="Pago", monto=-pagos.total, fecha=pagos.vence)[["fecha", "tipo", "monto"]],
    ]).sort_values("fecha")
    for _, row in movimientos.iterrows():
        saldo += row.monto
        movs.append({"Fecha": max(row.fecha, TODAY), "Saldo proyectado": saldo})
    st.plotly_chart(px.line(pd.DataFrame(movs), x="Fecha", y="Saldo proyectado", markers=True), width="stretch")
    st.markdown('<div class="cta"><h3>🚀 ¿Te gustaría probar Control Pyme con tu negocio?</h3><p>Únete al grupo Beta. No necesitas entregar información financiera real en esta etapa.</p></div>', unsafe_allow_html=True)
    st.link_button("Quiero participar en la Beta", "?start=beta", type="primary", width="stretch")

elif menu == "💬 Diagnóstico Pyme":
    st.title("💬 Diagnóstico Pyme")
    st.caption("En 2–3 minutos queremos entender cómo administras tu negocio y mostrarte dónde Control Pyme puede ayudarte más.")
    st.caption("🔒 Solo pedimos información general. No necesitamos RUT, claves, cuentas bancarias ni saldos reales.")
    with st.form("diagnostico"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Tu nombre *", max_chars=120)
        email = c2.text_input("Correo *", max_chars=180)
        c3, c4 = st.columns(2)
        whatsapp = c3.text_input("WhatsApp", max_chars=60)
        empresa = c4.text_input("Nombre de la empresa", max_chars=180)
        c5, c6 = st.columns(2)
        rubro = c5.selectbox("Rubro", ["Servicios", "Comercio/Distribución", "Construcción/Instalaciones", "Salud/Insumos médicos", "Logística/Transporte", "Consultoría", "Otro"])
        trabajadores = c6.selectbox("Trabajadores", ["1", "2–5", "6–10", "11–25", "26–50", "Más de 50"])
        ventas_mes = st.selectbox("Ventas mensuales aproximadas", ["Menos de $5 MM", "$5–15 MM", "$15–50 MM", "$50–150 MM", "Más de $150 MM", "Prefiero no indicar"])
        sistema = st.multiselect("¿Cómo administras hoy?", ["Excel", "Contador", "ERP", "Software de facturación", "Cuaderno/WhatsApp", "Otro"])
        dolor = st.selectbox("¿Cuál es hoy tu principal problema?", ["Caja y liquidez", "Cobranza", "Saber mi rentabilidad", "Costos y gastos", "Inventario", "Presupuesto/forecast", "Contratos/Legal", "Orden general del negocio"])
        credito = st.radio("¿Vendes a crédito?", ["Sí", "No", "A veces"], horizontal=True)
        legal = st.radio("¿Te interesaría que Control Pyme analice contratos y vencimientos?", ["Sí", "No", "Tal vez"], horizontal=True)
        precio = st.selectbox("Si resolviera tu principal problema, ¿qué rango mensual te parecería razonable?", ["Hasta $19.990", "$20.000–39.990", "$40.000–69.990", "Más de $70.000", "Aún no pagaría"])
        abierto = st.text_area("Cuéntanos en una frase qué es lo más difícil de administrar hoy", max_chars=1200)
        consentimiento = st.checkbox("Acepto que Control Pyme almacene estas respuestas para generar el diagnóstico, validar la Beta y contactarme sobre el producto.")
        enviar = st.form_submit_button("Generar mi diagnóstico", type="primary", width="stretch")
    if enviar:
        if len(nombre.strip()) < 2:
            st.error("Escribe tu nombre para continuar.")
        elif not valid_email(email):
            st.error("Revisa el correo. Debe tener un formato como nombre@empresa.cl.")
        elif not consentimiento:
            st.error("Necesitamos tu consentimiento para guardar el diagnóstico.")
        else:
            riesgo_caja = "Alto" if dolor in ["Caja y liquidez", "Cobranza"] or credito == "Sí" else "Medio"
            st.success("✅ Diagnóstico generado")
            a, b, c = st.columns(3)
            a.metric("Riesgo de caja", riesgo_caja); b.metric("Prioridad", dolor); c.metric("Legal Pyme", legal)
            st.info(f"Tu foco inicial debería ser **{dolor}**. Control Pyme puede ayudarte con alertas, caja proyectada y acciones concretas sin depender de una planilla.")
            payload = {"nombre": clean(nombre,120), "email": clean(email.lower(),180), "telefono": clean(whatsapp,60), "empresa": clean(empresa,180), "rubro": rubro, "trabajadores": trabajadores, "ventas_mensuales": ventas_mes, "herramienta_actual": clean(", ".join(sistema),180), "dolor_principal": dolor, "vende_credito": credito, "interes_legal": legal, "disposicion_pago": precio, "comentario": clean(abierto,1200), "consentimiento": True}
            ok, msg = save_lead(payload)
            if ok:
                funnel_event("diagnostico_completado")
                activate_quick_feedback("diagnóstico")
                st.caption("Tus respuestas quedaron registradas para la Beta.")
            elif "Ya existe" in msg:
                activate_quick_feedback("diagnóstico")
                st.caption("ℹ️ Ese correo ya había completado el diagnóstico. No creamos un duplicado.")
            else:
                st.warning(f"El diagnóstico se generó, pero no pudimos guardar las respuestas. {msg}")
            st.link_button("🚀 Siguiente: participar en la Beta", "?start=beta", type="primary", width="stretch")

elif menu == "🚀 Participar en la Beta":
    st.title("🚀 Participa en Control Pyme Beta")
    st.caption("Buscamos un grupo pequeño de Pymes para probar el producto y ayudarnos a priorizar las funciones que realmente generan valor.")
    st.success("Los participantes Beta tendrán acceso anticipado y condiciones preferentes de lanzamiento. Esta solicitud no genera ningún cobro.")
    with st.form("beta_interes"):
        c1, c2 = st.columns(2)
        beta_nombre = c1.text_input("Nombre *", max_chars=120); beta_email = c2.text_input("Correo *", max_chars=180)
        c3, c4 = st.columns(2)
        beta_telefono = c3.text_input("WhatsApp", max_chars=60); beta_empresa = c4.text_input("Empresa", max_chars=180)
        beta_plan = st.selectbox("¿Qué versión te interesaría probar?", ["Aún no sé", "Control", "Control Pro", "Control 360 + Legal"])
        beta_motivo = st.text_area("¿Qué problema te gustaría resolver primero con Control Pyme?", max_chars=1200)
        beta_consent = st.checkbox("Acepto que Control Pyme almacene estos datos y me contacte para coordinar la Beta.")
        beta_send = st.form_submit_button("Quiero participar en la Beta", type="primary", width="stretch")
    if beta_send:
        if len(beta_nombre.strip()) < 2: st.error("Escribe tu nombre para continuar.")
        elif not valid_email(beta_email): st.error("Ingresa un correo válido.")
        elif not beta_consent: st.error("Necesitamos tu consentimiento para registrarte en la Beta.")
        else:
            ok, msg = save_beta_interest({"nombre":clean(beta_nombre,120),"email":clean(beta_email.lower(),180),"telefono":clean(beta_telefono,60),"empresa":clean(beta_empresa,180),"motivo":clean(beta_motivo,1200),"plan_interes":beta_plan,"consentimiento":True})
            if ok:
                funnel_event("beta_interes")
                activate_quick_feedback("registro Beta")
                st.success("✅ ¡Listo! Ya estás en la lista de Control Pyme Beta. Te contactaremos para coordinar los próximos pasos.")
                st.link_button("⭐ Cuéntanos qué te pareció la demo", "?start=feedback", width="stretch")
            elif "Ya existe" in msg:
                activate_quick_feedback("registro Beta")
                st.info("✅ Ese correo ya está inscrito en la Beta. No necesitas registrarte de nuevo.")
            else: st.error(msg)

elif menu == "💵 Caja":
    st.title("💵 Caja proyectada"); st.caption("Escenario completamente ficticio para mostrar cómo funcionará el módulo.")
    st.metric("Caja hoy", money(KPIS["caja"])); st.warning("Una Pyme puede tener utilidad y aun así quedarse sin caja. Control Pyme prioriza liquidez y fechas de cobro/pago.")
    tabla = pd.concat([ventas.assign(Tipo="Cobro", Entidad=ventas.cliente, Monto=ventas.total, Fecha=ventas.vence)[["Fecha","Tipo","Entidad","Monto"]], pagos.assign(Tipo="Pago", Entidad=pagos.proveedor, Monto=-pagos.total, Fecha=pagos.vence)[["Fecha","Tipo","Entidad","Monto"]]]).sort_values("Fecha")
    st.dataframe(tabla, hide_index=True, width="stretch"); st.link_button("⭐ ¿Te serviría este módulo? Danos feedback", "?start=feedback", width="stretch")

elif menu == "🚨 Alertas":
    st.title("🚨 Alertas y cobranza"); st.caption("Clientes y montos ficticios de demostración.")
    x=ventas.copy(); x["Días vencido"]=(TODAY-x.vence).dt.days; x["Tramo"]=pd.cut(x["Días vencido"],[-10000,0,30,60,90,10000],labels=["Por vencer","1–30","31–60","61–90","+90"])
    st.dataframe(x[["cliente","total","vence","Días vencido","Tramo","margen"]], hide_index=True, width="stretch")
    st.info("Próxima capa: recordatorios de cobranza, promesas de pago y preparación automática de WhatsApp/email."); st.link_button("⭐ ¿Te serviría este módulo? Danos feedback", "?start=feedback", width="stretch")

elif menu == "📑 Legal Pyme":
    st.title("📑 Legal Pyme"); st.caption("Vista conceptual de una futura capa preventiva para contratos y obligaciones.")
    st.warning("🔒 La carga de documentos reales está DESACTIVADA en esta Beta pública. No subas contratos, liquidaciones, cédulas ni documentos con información confidencial.")
    st.subheader("Ejemplo ficticio de análisis"); c1,c2,c3=st.columns(3); c1.metric("Renovación automática","Sí","Avisar 60 días antes"); c2.metric("Riesgo","Medio","1 cláusula a revisar"); c3.metric("Próximo hito","15 oct","Fecha ficticia")
    st.markdown("**Lo que buscará la versión completa:** partes, duración, renovación, multas, obligaciones, fechas críticas, reajustes, garantías y un semáforo de riesgo.")
    st.info("Legal Pyme será una herramienta de apoyo y detección de riesgos; los casos relevantes deberán poder escalarse a un abogado."); st.link_button("⭐ Opinar sobre Legal Pyme", "?start=feedback", width="stretch")

elif menu == "💳 Planes Beta":
    st.title("💳 Planes Beta"); st.caption("Precios de referencia que estamos validando. Todavía no existe cobro dentro de esta Beta pública.")
    c1,c2,c3=st.columns(3)
    with c1: st.subheader("Control"); st.metric("$19.990 + IVA","/ mes"); st.write("Dashboard · Caja · CxC/CxP · Alertas")
    with c2: st.subheader("Control Pro"); st.metric("$39.990 + IVA","/ mes"); st.write("Cobranza inteligente · Presupuesto · Forecast · Bancos")
    with c3: st.subheader("Control 360"); st.metric("$69.990 + IVA","/ mes"); st.write("Todo Pro · Legal Pyme · automatización avanzada")
    st.link_button("🚀 Quiero participar en la Beta", "?start=beta", type="primary", width="stretch")

elif menu == "⭐ Feedback Beta":
    st.title("⭐ Ayúdanos a mejorar Control Pyme"); st.caption("Toma menos de un minuto. Este feedback es una de las partes más importantes de la Beta.")
    with st.form("feedback_beta"):
        puntuacion=st.slider("En general, ¿qué nota le pondrías a esta Beta?",1,5,4)
        utilidad=st.radio("¿Te serviría una herramienta así en tu negocio?",["Sí","Parcialmente","No"],horizontal=True)
        parte_util=st.selectbox("¿Qué parte te pareció más útil?",["Dashboard/Inicio","Diagnóstico","Caja","Alertas/Cobranza","Legal Pyme","Planes","Otra"])
        comentario=st.text_area("¿Qué faltó, qué no entendiste o qué función debería existir sí o sí?",max_chars=1200)
        feedback_email=st.text_input("Correo (opcional, si quieres que podamos preguntarte más)",max_chars=180)
        feedback_consent=st.checkbox("Acepto que Control Pyme almacene este feedback para mejorar la Beta.")
        feedback_send=st.form_submit_button("Enviar feedback",type="primary",width="stretch")
    if feedback_send:
        if feedback_email.strip() and not valid_email(feedback_email): st.error("El correo opcional no tiene un formato válido.")
        elif not feedback_consent: st.error("Necesitamos tu consentimiento para guardar el feedback.")
        else:
            ok,msg=save_feedback({"puntuacion":int(puntuacion),"utilidad":utilidad,"parte_util":clean(parte_util,120),"comentario":clean(comentario,1200),"email":clean(feedback_email.lower(),180),"consentimiento":True})
            if ok:
                funnel_event("feedback_enviado"); st.session_state.quick_feedback_done=True; st.success("🙌 Gracias. Tu opinión quedó registrada y nos ayuda a decidir qué construir primero.")
            else: st.error(msg)

else:
    st.title("🔒 Privacidad de la Beta"); st.caption("Versión simple y transparente para esta etapa de validación.")
    st.markdown("""
**Qué guardamos:** si completas formularios, podemos guardar tu nombre, correo, teléfono, empresa, rubro, tamaño aproximado, respuestas del diagnóstico, interés en la Beta y feedback. También guardamos el origen de la invitación (por ejemplo, LinkedIn o WhatsApp) para medir qué canal funciona mejor.

**Para qué lo usamos:** generar y validar el diagnóstico, entender qué problemas tienen las Pymes, mejorar Control Pyme y contactarte sobre la Beta cuando hayas dado tu consentimiento.

**Qué NO necesitamos en esta Beta:** claves, contraseñas, datos bancarios, cartolas, RUT personales, contratos reales, liquidaciones ni otros documentos sensibles. No los ingreses.

**Dónde se almacenan los registros de la Beta:** en una base de datos protegida de Supabase. El panel de administración no está abierto a lectura pública.

**Compartición:** no vendemos tus datos a terceros ni los usamos para publicidad de terceros.

**Plazo de esta Beta:** como política de la etapa de validación, conservaremos los datos por un máximo de 12 meses desde su registro, salvo que pases a ser cliente o solicites antes su eliminación.

**Corrección o eliminación:** puedes pedir que corrijamos o eliminemos tus datos contactándonos por el mismo canal por el que recibiste la invitación a esta Beta.
""")
    st.info("Si solo quieres mirar la demo, puedes navegar sin completar ningún formulario.")

if st.session_state.get("quick_feedback_context") and not st.session_state.get("quick_feedback_done", False):
    st.markdown('<div class="quick-feedback"><b>Una última pregunta de 2 segundos:</b><br>¿Te serviría Control Pyme en un negocio real?</div>', unsafe_allow_html=True)
    q1,q2,q3=st.columns(3)
    if q1.button("👍 Sí", width="stretch"):
        funnel_event("feedback_rapido_si"); st.session_state.quick_feedback_done=True; st.success("¡Gracias! 🙌"); st.rerun()
    if q2.button("🤔 Tal vez", width="stretch"):
        funnel_event("feedback_rapido_tal_vez"); st.session_state.quick_feedback_done=True; st.success("¡Gracias! 🙌"); st.rerun()
    if q3.button("👎 No", width="stretch"):
        funnel_event("feedback_rapido_no"); st.session_state.quick_feedback_done=True; st.success("¡Gracias por decirlo! 🙌"); st.rerun()
    st.caption("Respuesta anónima de sesión; no agrega nuevos datos personales.")

st.divider()
st.caption("Control Pyme Beta · El control de tu negocio sin vivir en planillas. · 🧪 Datos de demo ficticios")
