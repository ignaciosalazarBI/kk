from __future__ import annotations

from datetime import date, timedelta
import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Control Pyme Beta", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1.3rem; padding-bottom:3rem; max-width:1400px}
[data-testid="stSidebar"] {min-width:230px; max-width:230px}
.kpi {border:1px solid #e7e7e7;border-radius:16px;padding:18px;background:white;min-height:118px;box-shadow:0 2px 10px rgba(0,0,0,.035)}
.kpi .label {font-size:.83rem;color:#68707a;margin-bottom:7px}
.kpi .value {font-size:1.72rem;font-weight:800;line-height:1.05}
.kpi .sub {font-size:.78rem;color:#7a818a;margin-top:7px}
.action {padding:14px 16px;border-radius:13px;background:#fff7ed;border:1px solid #fed7aa;margin-bottom:9px}
.good {padding:14px 16px;border-radius:13px;background:#ecfdf5;border:1px solid #a7f3d0;margin-bottom:9px}
.hero {padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,#f8fafc,#eef2ff);border:1px solid #e5e7eb;margin-bottom:16px}
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


def kpi(label, value, sub=""):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def save_lead(payload: dict) -> tuple[bool, str]:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_ANON_KEY", "")
    except Exception:
        url, key = "", ""
    if not url or not key:
        return False, "Supabase aún no está configurado en Secrets."
    try:
        r = requests.post(
            f"{url.rstrip('/')}/rest/v1/leads",
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=minimal"},
            data=json.dumps(payload, ensure_ascii=False), timeout=12,
        )
        if r.status_code in (200, 201, 204):
            return True, "Registro guardado."
        return False, f"Supabase respondió {r.status_code}."
    except Exception as exc:
        return False, f"No se pudo guardar: {exc}"


# Datos demo diseñados para explicar el producto, no datos reales.
TODAY = pd.Timestamp.today().normalize()
ventas = pd.DataFrame([
    {"cliente":"Cliente Andes","total":1180000,"vence":TODAY-pd.Timedelta(days=47),"margen":0.31},
    {"cliente":"Servicios Norte","total":730000,"vence":TODAY-pd.Timedelta(days=8),"margen":0.54},
    {"cliente":"Comercial Sur","total":590000,"vence":TODAY+pd.Timedelta(days=5),"margen":0.68},
])
pagos = pd.DataFrame([
    {"proveedor":"Proveedor A","total":320000,"vence":TODAY+pd.Timedelta(days=4)},
    {"proveedor":"Proveedor B","total":180000,"vence":TODAY+pd.Timedelta(days=12)},
])

KPIS = {
    "ventas": 3_100_000,
    "margen": 2_040_000,
    "margen_pct": .658,
    "caja": -190_000,
    "por_cobrar": float(ventas.total.sum()),
    "costo_ventas": 1_060_000,
}

menu = st.sidebar.radio("Control Pyme", ["🏠 Inicio", "💬 Diagnóstico Pyme", "💵 Caja", "🚨 Alertas", "📑 Legal Pyme", "💳 Planes Beta"])
st.sidebar.caption("Beta pública · Chile")

if menu == "🏠 Inicio":
    st.markdown('<div class="hero"><h2 style="margin:0">Hoy en tu negocio</h2><div style="color:#667085;margin-top:6px">Entiende en segundos cómo estás y qué deberías hacer primero.</div></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]: kpi("Ventas mes", money(KPIS["ventas"]), "Neto")
    with cols[1]: kpi("Margen bruto", f'{KPIS["margen_pct"]:.1%}'.replace(".", ","), money(KPIS["margen"]))
    with cols[2]: kpi("Caja disponible", money(KPIS["caja"]), "Atención inmediata")
    with cols[3]: kpi("Por cobrar", money(KPIS["por_cobrar"]), "3 documentos")
    with cols[4]: kpi("Costo ventas", money(KPIS["costo_ventas"]), "Mes actual")

    st.subheader("🚨 Requiere acción")
    vencido = ventas[ventas.vence < TODAY]
    st.markdown(f'<div class="action"><b>Caja bajo mínimo.</b> Tienes {money(vencido.total.sum())} vencidos. Prioriza cobranza antes de pagos no críticos.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="action"><b>{len(vencido)} clientes con documentos vencidos.</b> El más antiguo lleva {(TODAY-vencido.vence.min()).days} días.</div>', unsafe_allow_html=True)
    bajo = ventas[ventas.margen < .35]
    if not bajo.empty:
        st.markdown(f'<div class="action"><b>Margen bajo.</b> Revisa {bajo.iloc[0].cliente}: margen estimado {bajo.iloc[0].margen:.0%}.</div>', unsafe_allow_html=True)

    st.subheader("Próximos 30 días")
    cobros_30 = ventas[(ventas.vence >= TODAY) & (ventas.vence <= TODAY+pd.Timedelta(days=30))].total.sum() + vencido.total.sum()
    pagos_30 = pagos[pagos.vence <= TODAY+pd.Timedelta(days=30)].total.sum()
    caja_30 = KPIS["caja"] + cobros_30 - pagos_30
    a,b,c = st.columns(3)
    with a: kpi("Cobros esperados", money(cobros_30), "Incluye vencidos")
    with b: kpi("Pagos esperados", money(pagos_30), "30 días")
    with c: kpi("Caja proyectada 30d", money(caja_30), "Si cobras/pagas según calendario")

    movs = []
    saldo = KPIS["caja"]
    for _,r in pd.concat([
        ventas.assign(tipo="Cobro", monto=ventas.total, fecha=ventas.vence)[["fecha","tipo","monto"]],
        pagos.assign(tipo="Pago", monto=-pagos.total, fecha=pagos.vence)[["fecha","tipo","monto"]]
    ]).sort_values("fecha").iterrows():
        saldo += r.monto
        movs.append({"Fecha":max(r.fecha,TODAY),"Saldo proyectado":saldo})
    if movs:
        chart = pd.DataFrame(movs)
        fig = px.line(chart, x="Fecha", y="Saldo proyectado", markers=True)
        st.plotly_chart(fig, width="stretch")

elif menu == "💬 Diagnóstico Pyme":
    st.title("💬 Diagnóstico Pyme")
    st.caption("En 2–3 minutos queremos entender cómo administras tu negocio y mostrarte dónde Control Pyme puede ayudarte más.")
    with st.form("diagnostico"):
        c1,c2 = st.columns(2)
        nombre = c1.text_input("Tu nombre *")
        email = c2.text_input("Correo *")
        c3,c4 = st.columns(2)
        whatsapp = c3.text_input("WhatsApp")
        empresa = c4.text_input("Nombre de la empresa")
        c5,c6 = st.columns(2)
        rubro = c5.selectbox("Rubro", ["Servicios","Comercio/Distribución","Construcción/Instalaciones","Salud/Insumos médicos","Logística/Transporte","Consultoría","Otro"])
        trabajadores = c6.selectbox("Trabajadores", ["1","2–5","6–10","11–25","26–50","Más de 50"])
        ventas_mes = st.selectbox("Ventas mensuales aproximadas", ["Menos de $5 MM","$5–15 MM","$15–50 MM","$50–150 MM","Más de $150 MM","Prefiero no indicar"])
        sistema = st.multiselect("¿Cómo administras hoy?", ["Excel","Contador","ERP","Software de facturación","Cuaderno/WhatsApp","Otro"])
        dolor = st.selectbox("¿Cuál es hoy tu principal problema?", ["Caja y liquidez","Cobranza","Saber mi rentabilidad","Costos y gastos","Inventario","Presupuesto/forecast","Contratos/Legal","Orden general del negocio"])
        credito = st.radio("¿Vendes a crédito?", ["Sí","No","A veces"], horizontal=True)
        legal = st.radio("¿Te interesaría que Control Pyme analice contratos y vencimientos?", ["Sí","No","Tal vez"], horizontal=True)
        precio = st.selectbox("Si resolviera tu principal problema, ¿qué rango mensual te parecería razonable?", ["Hasta $19.990","$20.000–39.990","$40.000–69.990","Más de $70.000","Aún no pagaría"])
        abierto = st.text_area("Cuéntanos en una frase qué es lo más difícil de administrar hoy")
        consentimiento = st.checkbox("Acepto que Control Pyme almacene estas respuestas para generar el diagnóstico y contactarme sobre la beta.")
        enviar = st.form_submit_button("Generar mi diagnóstico", type="primary", width="stretch")

    if enviar:
        if not nombre.strip() or not email.strip() or not consentimiento:
            st.error("Completa nombre, correo y consentimiento para continuar.")
        else:
            riesgo_caja = "Alto" if dolor in ["Caja y liquidez","Cobranza"] or credito == "Sí" else "Medio"
            st.success("Diagnóstico generado")
            a,b,c = st.columns(3)
            a.metric("Riesgo de caja", riesgo_caja)
            b.metric("Prioridad", dolor)
            c.metric("Legal Pyme", legal)
            st.info(f"Tu foco inicial debería ser **{dolor}**. Control Pyme puede darte alertas, caja proyectada y acciones concretas sin depender de una planilla.")
            payload = {
                "nombre": nombre.strip(), "email": email.strip(), "telefono": whatsapp.strip(), "empresa": empresa.strip(),
                "rubro": rubro, "trabajadores": trabajadores, "ventas_mensuales": ventas_mes,
                "herramienta_actual": ", ".join(sistema), "dolor_principal": dolor,
                "vende_credito": credito, "interes_legal": legal, "disposicion_pago": precio,
                "comentario": abierto.strip(), "consentimiento": True,
            }
            ok,msg = save_lead(payload)
            if ok: st.caption("✅ Tus respuestas quedaron registradas para la Beta.")
            else: st.caption(f"ℹ️ Diagnóstico listo. {msg}")

elif menu == "💵 Caja":
    st.title("💵 Caja proyectada")
    st.metric("Caja hoy", money(KPIS["caja"]))
    st.warning("Una Pyme puede tener utilidad y aun así quedarse sin caja. Aquí priorizamos liquidez y fechas de cobro/pago.")
    tabla = pd.concat([
        ventas.assign(Tipo="Cobro", Entidad=ventas.cliente, Monto=ventas.total, Fecha=ventas.vence)[["Fecha","Tipo","Entidad","Monto"]],
        pagos.assign(Tipo="Pago", Entidad=pagos.proveedor, Monto=-pagos.total, Fecha=pagos.vence)[["Fecha","Tipo","Entidad","Monto"]],
    ]).sort_values("Fecha")
    st.dataframe(tabla, hide_index=True, width="stretch")

elif menu == "🚨 Alertas":
    st.title("🚨 Alertas y cobranza")
    x = ventas.copy()
    x["Días vencido"] = (TODAY-x.vence).dt.days
    x["Tramo"] = pd.cut(x["Días vencido"], [-10_000,0,30,60,90,10_000], labels=["Por vencer","1–30","31–60","61–90","+90"])
    st.dataframe(x[["cliente","total","vence","Días vencido","Tramo","margen"]], hide_index=True, width="stretch")
    st.info("Próxima capa: recordatorios de cobranza, promesas de pago y preparación automática de WhatsApp/email.")

elif menu == "📑 Legal Pyme":
    st.title("📑 Legal Pyme")
    st.caption("Demo conceptual: prevención y organización jurídica para pequeños negocios.")
    st.file_uploader("Sube un contrato para analizar (demo)", type=["pdf","docx"])
    st.markdown("**Qué entregará la versión completa:** resumen, partes, duración, renovación automática, multas, obligaciones, fechas críticas, semáforo de riesgo y preguntas sobre el documento.")
    st.warning("Legal Pyme será una herramienta de apoyo y detección de riesgos; los casos relevantes deberán poder escalarse a un abogado.")

else:
    st.title("💳 Planes Beta")
    st.caption("Hipótesis de precios que validaremos con los primeros usuarios.")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.subheader("Control")
        st.metric("$19.990 + IVA", "/ mes")
        st.write("Dashboard · Caja · CxC/CxP · Alertas")
    with c2:
        st.subheader("Control Pro")
        st.metric("$39.990 + IVA", "/ mes")
        st.write("Cobranza inteligente · Presupuesto · Forecast · Bancos")
    with c3:
        st.subheader("Control 360")
        st.metric("$69.990 + IVA", "/ mes")
        st.write("Todo Pro · Legal Pyme · automatización avanzada")
    st.info("El botón de pago real se integrará después de validar el flujo completo de la Beta.")

st.divider()
st.caption("Control Pyme Beta · El control de tu negocio sin vivir en planillas.")
