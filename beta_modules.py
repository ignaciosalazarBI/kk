from __future__ import annotations

import json
import re
import uuid

import pandas as pd
import requests
import streamlit as st


def _clean(value: str, limit: int) -> str:
    return " ".join(str(value or "").strip().split())[:limit]


def _secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def _slug(text: str) -> str:
    repl = text.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return re.sub(r"[^a-z0-9]+", "_", repl).strip("_")


def _money(value: float) -> str:
    sign = "-" if value < 0 else ""
    value = abs(float(value))
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f} MM".replace(".", ",")
    if value >= 1_000:
        return f"{sign}${value / 1_000:.0f} mil"
    return f"{sign}${value:,.0f}".replace(",", ".")


def _init_tracking() -> dict:
    if "tracking" not in st.session_state:
        st.session_state.tracking = {
            "utm_source": _clean(st.query_params.get("utm_source", "direct"), 80) or "direct",
            "utm_medium": _clean(st.query_params.get("utm_medium", "none"), 80) or "none",
            "utm_campaign": _clean(st.query_params.get("utm_campaign", "beta_publica"), 120) or "beta_publica",
        }
    if "beta_session_id" not in st.session_state:
        st.session_state.beta_session_id = str(uuid.uuid4())
    return dict(st.session_state.tracking)


def _event(name: str) -> None:
    tracking = _init_tracking()
    url, key = _secret("SUPABASE_URL"), _secret("SUPABASE_ANON_KEY")
    if not url or not key:
        return
    payload = {
        "session_id": st.session_state.beta_session_id,
        "evento": _clean(name, 100),
        "utm_source": tracking["utm_source"],
        "utm_medium": tracking["utm_medium"],
        "utm_campaign": tracking["utm_campaign"],
    }
    try:
        requests.post(
            f"{url.rstrip('/')}/rest/v1/eventos_beta",
            headers={"apikey": key, "Content-Type": "application/json", "Prefer": "return=minimal"},
            data=json.dumps(payload, ensure_ascii=False),
            timeout=4,
        )
    except Exception:
        pass


def _track_page(module: str) -> None:
    slug = _slug(module)
    key = f"seen_module_page_{slug}"
    if not st.session_state.get(key):
        _event(f"pantalla_{slug}")
        st.session_state[key] = True


def _header(title: str, subtitle: str) -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width:1180px;padding-top:2rem;padding-bottom:3rem}
        .beta-note {border:1px solid #f59e0b;background:#fffbeb;border-radius:14px;padding:12px 15px;margin:8px 0 18px;line-height:1.45;font-size:.92rem}
        .insight {border:1px solid #bfdbfe;background:#f8fbff;border-radius:18px;padding:18px 20px;margin:14px 0 18px;line-height:1.5}
        @media(max-width:768px){.block-container{padding-left:1rem;padding-right:1rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title(title)
    st.caption(subtitle)
    st.markdown('<div class="beta-note"><b>🧪 DEMO PÚBLICA · DATOS FICTICIOS</b><br>Esta vista sirve para validar el producto. No ingreses información real ni sensible.</div>', unsafe_allow_html=True)


def _footer() -> None:
    st.divider()
    st.page_link("app.py", label="← Volver a Control Pyme", icon="🏠")
    st.caption("Beta pública · Información ficticia · Funcionalidades sujetas a validación")


def render_cobranza() -> None:
    _track_page("cobranza")
    _header("📞 Cobranza", "Prioriza quién cobrar hoy, cuánto está vencido y dónde está concentrado el riesgo.")
    data = pd.DataFrame([
        {"Cliente":"Cliente Andes","Documento":"F-1048","Monto":1_180_000,"Días vencido":47,"Promesa":"Sin compromiso","Prioridad":"🔴 Alta"},
        {"Cliente":"Servicios Norte","Documento":"F-1071","Monto":730_000,"Días vencido":8,"Promesa":"25-08","Prioridad":"🟠 Media"},
        {"Cliente":"Comercial Sur","Documento":"F-1092","Monto":590_000,"Días vencido":0,"Promesa":"Vence en 5 días","Prioridad":"🟢 Normal"},
        {"Cliente":"Constructora Delta","Documento":"F-1033","Monto":420_000,"Días vencido":63,"Promesa":"Recontactar","Prioridad":"🔴 Alta"},
    ])
    vencido = float(data.loc[data["Días vencido"] > 0, "Monto"].sum())
    a,b,c,d=st.columns(4)
    a.metric("Por cobrar", _money(data["Monto"].sum()))
    b.metric("Vencido", _money(vencido), f"{vencido/data['Monto'].sum():.0%} de la cartera")
    c.metric("Clientes críticos", "2", "> 30 días")
    d.metric("Promesas activas", "1", "Próximos 7 días")
    st.markdown('<div class="insight"><b>🤖 Acción sugerida</b><br>Contacta primero a Cliente Andes y Constructora Delta: concentran la mayor mora y superan 30 días vencidos. Si recuperas ambos saldos, reducirías fuertemente el riesgo de caja.</div>', unsafe_allow_html=True)
    tab1,tab2=st.tabs(["📋 Cartera", "⏳ Aging"])
    with tab1:
        view=data.copy(); view["Monto"]=view["Monto"].map(_money)
        st.dataframe(view, hide_index=True, width="stretch")
    with tab2:
        aging=pd.DataFrame({"Tramo":["Por vencer","1–30 días","31–60 días","+60 días"],"Monto":[590_000,730_000,1_180_000,420_000]})
        st.bar_chart(aging.set_index("Tramo")/1_000_000)
        aging["Monto"]=aging["Monto"].map(_money); st.dataframe(aging,hide_index=True,width="stretch")
    st.info("Próxima etapa: recordatorios automáticos, promesas de pago, plantillas WhatsApp/email y seguimiento de gestión.")
    _footer()


def render_sii() -> None:
    _track_page("sii")
    _header("🧾 SII", "Ordena documentos y obligaciones tributarias sin reemplazar a tu contador.")
    a,b,c,d=st.columns(4)
    a.metric("DTE del mes", "86", "Ejemplo")
    b.metric("Documentos observados", "3", "Revisar")
    c.metric("IVA estimado", _money(1_280_000), "Referencial")
    d.metric("Próximo vencimiento", "12 días", "Ficticio")
    st.markdown('<div class="insight"><b>🤖 Revisión sugerida</b><br>Hay 3 documentos que no cuadran con el registro interno. Revísalos antes del cierre para evitar diferencias entre compras, ventas y contabilidad.</div>', unsafe_allow_html=True)
    docs=pd.DataFrame([
        {"Tipo":"Factura venta","Folio":"1842","Emisor / Cliente":"Cliente Andes","Monto":1_180_000,"Estado":"✅ OK"},
        {"Tipo":"Factura compra","Folio":"7781","Emisor / Cliente":"Proveedor Uno","Monto":640_000,"Estado":"⚠️ Sin clasificar"},
        {"Tipo":"Nota de crédito","Folio":"212","Emisor / Cliente":"Comercial Sur","Monto":125_000,"Estado":"⚠️ Revisar referencia"},
        {"Tipo":"Factura compra","Folio":"7804","Emisor / Cliente":"Proveedor Dos","Monto":410_000,"Estado":"✅ OK"},
    ])
    docs["Monto"]=docs["Monto"].map(_money)
    st.subheader("Documentos que requieren atención")
    st.dataframe(docs,hide_index=True,width="stretch")
    st.warning("Esta Beta no se conecta al SII ni solicita clave tributaria. Una integración real requerirá autorización, controles de seguridad y cumplimiento aplicable.")
    _footer()


def render_marketing() -> None:
    _track_page("marketing")
    _header("📣 Marketing y ventas", "Mide si el dinero invertido en campañas realmente genera clientes y ventas.")
    campaigns=pd.DataFrame([
        {"Campaña":"Instagram Agosto","Inversión":350_000,"Leads":48,"Clientes":9,"Ventas":2_100_000},
        {"Campaña":"Google Búsqueda","Inversión":420_000,"Leads":31,"Clientes":7,"Ventas":2_450_000},
        {"Campaña":"Facebook Remarketing","Inversión":180_000,"Leads":22,"Clientes":3,"Ventas":720_000},
    ])
    campaigns["CPL"]=campaigns["Inversión"]/campaigns["Leads"]
    campaigns["ROAS"]=campaigns["Ventas"]/campaigns["Inversión"]
    investment=float(campaigns["Inversión"].sum()); sales=float(campaigns["Ventas"].sum())
    a,b,c,d=st.columns(4)
    a.metric("Inversión",_money(investment))
    b.metric("Leads",int(campaigns["Leads"].sum()),f"CPL promedio {_money(investment/campaigns['Leads'].sum())}")
    c.metric("Clientes nuevos",int(campaigns["Clientes"].sum()))
    d.metric("Ventas atribuidas",_money(sales),f"ROAS {sales/investment:.1f}x")
    st.markdown('<div class="insight"><b>🤖 Recomendación</b><br>Google tiene el mejor retorno por peso invertido, mientras Facebook Remarketing presenta el ROAS más bajo. Antes de aumentar presupuesto, conviene revisar segmentación y conversión de esa campaña.</div>', unsafe_allow_html=True)
    view=campaigns.copy()
    for col in ["Inversión","Ventas","CPL"]: view[col]=view[col].map(_money)
    view["ROAS"]=view["ROAS"].map(lambda x:f"{x:.1f}x")
    st.dataframe(view,hide_index=True,width="stretch")
    st.bar_chart(campaigns.set_index("Campaña")[["Ventas","Inversión"]]/1_000_000)
    _footer()


def render_inventario() -> None:
    _track_page("inventario")
    _header("📦 Inventario", "Detecta quiebres, exceso de stock y compras que deberías anticipar.")
    inv=pd.DataFrame([
        {"SKU":"A-100","Producto":"Producto Alpha","Stock":8,"Venta mensual":32,"Costo unitario":48_000,"Estado":"🔴 Quiebre próximo"},
        {"SKU":"B-240","Producto":"Producto Beta","Stock":74,"Venta mensual":28,"Costo unitario":31_000,"Estado":"🟢 Normal"},
        {"SKU":"C-310","Producto":"Producto Gamma","Stock":122,"Venta mensual":14,"Costo unitario":22_000,"Estado":"🟠 Exceso"},
        {"SKU":"D-450","Producto":"Producto Delta","Stock":19,"Venta mensual":25,"Costo unitario":65_000,"Estado":"🟡 Comprar pronto"},
    ])
    inv["Valor stock"]=inv["Stock"]*inv["Costo unitario"]
    inv["Días cobertura"]=(inv["Stock"]/(inv["Venta mensual"]/30)).round().astype(int)
    a,b,c,d=st.columns(4)
    a.metric("Valor inventario",_money(inv["Valor stock"].sum()))
    b.metric("SKU críticos","2","Comprar / quiebre")
    c.metric("Exceso de stock","1","Capital inmovilizado")
    d.metric("Cobertura Alpha","8 días","Riesgo")
    st.markdown('<div class="insight"><b>🤖 Reposición sugerida</b><br>Producto Alpha tiene solo 8 días de cobertura. Si el proveedor demora 12 días, deberías emitir la compra ahora. Producto Gamma muestra exceso y conviene frenar nuevas compras.</div>', unsafe_allow_html=True)
    view=inv.copy(); view["Costo unitario"]=view["Costo unitario"].map(_money); view["Valor stock"]=view["Valor stock"].map(_money)
    st.dataframe(view,hide_index=True,width="stretch")
    coverage=inv.set_index("Producto")[["Días cobertura"]]
    st.bar_chart(coverage)
    _footer()


def render_conciliacion() -> None:
    _track_page("conciliacion_bancaria")
    _header("🏦 Conciliación bancaria", "Cruza movimientos del banco con ventas, cobros y gastos y deja solo excepciones para revisión.")
    data=pd.DataFrame([
        {"Fecha":"18-08-2026","Movimiento":"Abono Cliente Andes","Banco":850_000,"Sistema":850_000,"Confianza":"99%","Estado":"✅ Conciliado"},
        {"Fecha":"18-08-2026","Movimiento":"Pago Proveedor A","Banco":-320_000,"Sistema":-320_000,"Confianza":"99%","Estado":"✅ Conciliado"},
        {"Fecha":"19-08-2026","Movimiento":"Transferencia recibida","Banco":330_000,"Sistema":0,"Confianza":"72%","Estado":"⚠️ Revisar"},
        {"Fecha":"20-08-2026","Movimiento":"Cargo plataforma","Banco":-49_990,"Sistema":0,"Confianza":"45%","Estado":"⚠️ Sin respaldo"},
    ])
    a,b,c,d=st.columns(4)
    a.metric("Movimientos banco","27")
    b.metric("Auto-conciliados","24","89%")
    c.metric("Excepciones","3","Revisar")
    d.metric("Diferencia",_money(330_000),"Antes de ajustes")
    st.markdown('<div class="insight"><b>🤖 Coincidencia probable</b><br>La transferencia de $330 mil podría corresponder a una cuenta por cobrar abierta por el mismo monto. La Beta solo muestra la lógica; una versión productiva requerirá reglas, auditoría y confirmación del usuario.</div>', unsafe_allow_html=True)
    view=data.copy(); view["Banco"]=view["Banco"].map(_money); view["Sistema"]=view["Sistema"].map(_money)
    st.dataframe(view,hide_index=True,width="stretch")
    st.info("MVP propuesto: importar cartola CSV/Excel → sugerir coincidencias por monto, fecha y referencia → confirmar excepciones → guardar reglas reutilizables.")
    _footer()


def render_legal() -> None:
    _track_page("legal")
    _header("⚖️ Legal", "Controla contratos, renovaciones, obligaciones y fechas críticas antes de que se conviertan en problemas.")
    contracts=pd.DataFrame([
        {"Contrato":"Arriendo bodega","Contraparte":"Inmobiliaria Centro","Vence":"15-10-2026","Aviso":"60 días","Riesgo":"🟠 Medio"},
        {"Contrato":"Servicio cliente Andes","Contraparte":"Cliente Andes","Vence":"31-12-2026","Aviso":"30 días","Riesgo":"🟢 Bajo"},
        {"Contrato":"Proveedor crítico","Contraparte":"Proveedor Uno","Vence":"05-09-2026","Aviso":"15 días","Riesgo":"🔴 Alto"},
    ])
    a,b,c,d=st.columns(4)
    a.metric("Contratos activos","12")
    b.metric("Próximos a vencer","2","< 60 días")
    c.metric("Riesgo alto","1")
    d.metric("Obligaciones abiertas","4")
    st.markdown('<div class="insight"><b>🤖 Alerta contractual</b><br>El contrato con Proveedor Uno vence pronto y presenta una obligación pendiente. Conviene revisar renovación, plazo de aviso y condiciones antes de quedar sin cobertura.</div>', unsafe_allow_html=True)
    st.dataframe(contracts,hide_index=True,width="stretch")
    st.warning("🔒 La carga y análisis de contratos reales está desactivada en la Beta pública. La información legal futura deberá tratarse con controles de acceso, cifrado y trazabilidad.")
    _footer()


def render_ia() -> None:
    _track_page("ia")
    _header("🤖 IA · Copiloto del negocio", "Cruza señales de todas las áreas y transforma datos en una lista corta de acciones para hoy.")
    st.subheader("Buenos días 👋 Hoy tienes 4 cosas importantes")
    actions=pd.DataFrame([
        {"Prioridad":"🔴 1","Área":"Cobranza","Acción":"Cobrar Cliente Andes y Constructora Delta","Impacto":"Recuperar hasta $1,60 MM"},
        {"Prioridad":"🟠 2","Área":"Inventario","Acción":"Reponer Producto Alpha","Impacto":"Evitar quiebre en 8 días"},
        {"Prioridad":"🟡 3","Área":"Marketing","Acción":"Revisar Facebook Remarketing","Impacto":"Mejorar retorno de campaña"},
        {"Prioridad":"🔵 4","Área":"Legal","Acción":"Revisar contrato Proveedor Uno","Impacto":"Evitar vencimiento sin renovación"},
    ])
    st.dataframe(actions,hide_index=True,width="stretch")
    a,b,c=st.columns(3)
    a.metric("Alertas críticas","2")
    b.metric("Caja potencial a recuperar",_money(1_600_000))
    c.metric("Decisiones sugeridas","4")
    st.markdown('<div class="insight"><b>Cómo funcionaría</b><br>La IA no reemplaza la decisión del dueño. Resume información de Finanzas, Cobranza, SII, Marketing, Inventario, Banco y Legal; explica por qué algo importa y propone una acción verificable.</div>', unsafe_allow_html=True)
    question=st.selectbox("Ejemplo: ¿qué quieres preguntarle al copiloto?",["¿Qué debería hacer hoy?","¿Dónde estoy perdiendo plata?","¿Qué cliente debería cobrar primero?","¿Qué riesgo viene en los próximos 30 días?"])
    responses={
        "¿Qué debería hacer hoy?":"Prioriza cobranza vencida y reposición de Alpha. Son las dos acciones con impacto más inmediato en caja y continuidad operacional.",
        "¿Dónde estoy perdiendo plata?":"La línea 'Otros' del módulo Finanzas tiene margen bajo y Facebook Remarketing presenta el menor retorno. Ambos merecen revisión antes de crecer.",
        "¿Qué cliente debería cobrar primero?":"Cliente Andes: $1,18 MM con 47 días de atraso. Después Constructora Delta: $420 mil con 63 días.",
        "¿Qué riesgo viene en los próximos 30 días?":"Quiebre de Producto Alpha y vencimiento del contrato de Proveedor Uno son las señales más cercanas.",
    }
    st.success(responses[question])
    st.caption("Respuesta demostrativa basada exclusivamente en datos ficticios precargados.")
    _footer()


RENDERERS = {
    "cobranza": render_cobranza,
    "sii": render_sii,
    "marketing": render_marketing,
    "inventario": render_inventario,
    "conciliacion": render_conciliacion,
    "legal": render_legal,
    "ia": render_ia,
}
