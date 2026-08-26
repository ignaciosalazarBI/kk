from __future__ import annotations

import json
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from design_system import ACCENT, DANGER, MUTED, POSITIVE, WARNING, hero, insight, section


def _secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def _config() -> tuple[str, str]:
    return _secret("SUPABASE_URL").rstrip("/"), _secret("SUPABASE_ANON_KEY")


def _money(value: float) -> str:
    value = float(value or 0)
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}${value:,.0f}".replace(",", ".")


def _auth_request(path: str, payload: dict) -> tuple[dict | None, str]:
    url, key = _config()
    if not url or not key:
        return None, "La autenticación todavía no está configurada."
    try:
        response = requests.post(
            f"{url}/auth/v1/{path}",
            headers={"apikey": key, "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )
        body = response.json() if response.content else {}
        if response.ok:
            return body, "ok"
        return None, str(body.get("msg") or body.get("error_description") or body.get("message") or "No pudimos completar la solicitud.")
    except Exception:
        return None, "No pudimos conectar con el servicio de acceso. Intenta nuevamente."


def _set_session(body: dict) -> bool:
    token = body.get("access_token")
    user = body.get("user") or {}
    if not token or not user.get("id"):
        return False
    st.session_state.finance_auth = {
        "access_token": token,
        "refresh_token": body.get("refresh_token", ""),
        "expires_at": body.get("expires_at"),
        "user": user,
    }
    return True


def _sign_out() -> None:
    auth = st.session_state.get("finance_auth") or {}
    url, key = _config()
    token = auth.get("access_token")
    if url and key and token:
        try:
            requests.post(
                f"{url}/auth/v1/logout",
                headers={"apikey": key, "Authorization": f"Bearer {token}"},
                timeout=6,
            )
        except Exception:
            pass
    st.session_state.pop("finance_auth", None)
    st.rerun()


def _db_request(method: str, table: str, *, params: dict | None = None, payload: dict | None = None, prefer: str | None = None) -> tuple[list | dict | None, str]:
    url, key = _config()
    auth = st.session_state.get("finance_auth") or {}
    token = auth.get("access_token")
    if not url or not key or not token:
        return None, "Sesión no disponible."
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    try:
        response = requests.request(
            method,
            f"{url}/rest/v1/{table}",
            headers=headers,
            params=params,
            data=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            timeout=15,
        )
        if response.status_code in (200, 201, 204):
            if not response.content:
                return [], "ok"
            return response.json(), "ok"
        if response.status_code in (401, 403):
            return None, "Tu sesión expiró o no tiene acceso a estos datos."
        try:
            body = response.json()
            message = body.get("message") or body.get("hint") or f"HTTP {response.status_code}"
        except Exception:
            message = f"HTTP {response.status_code}"
        return None, str(message)
    except Exception:
        return None, "No pudimos conectar con tus datos financieros."


def _get_profile() -> dict | None:
    data, _ = _db_request("GET", "finance_profiles", params={"select": "*", "limit": "1"})
    if isinstance(data, list) and data:
        return dict(data[0])
    return None


def _save_profile(name: str, initial_cash: float, monthly_goal: float) -> tuple[bool, str]:
    user = (st.session_state.get("finance_auth") or {}).get("user") or {}
    payload = {
        "user_id": user.get("id"),
        "business_name": name.strip()[:120],
        "currency": "CLP",
        "initial_cash": float(initial_cash),
        "monthly_revenue_goal": float(monthly_goal),
    }
    data, message = _db_request(
        "POST",
        "finance_profiles",
        payload=payload,
        prefer="resolution=merge-duplicates,return=representation",
    )
    return data is not None, message


def _transactions() -> pd.DataFrame:
    data, _ = _db_request(
        "GET",
        "finance_transactions",
        params={"select": "id,tx_date,kind,status,category,counterparty,amount,notes,created_at", "order": "tx_date.desc,created_at.desc"},
    )
    df = pd.DataFrame(data or [])
    if df.empty:
        return pd.DataFrame(columns=["id", "tx_date", "kind", "status", "category", "counterparty", "amount", "notes", "created_at"])
    df["tx_date"] = pd.to_datetime(df["tx_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def _add_transaction(tx_date: date, kind: str, status: str, category: str, counterparty: str, amount: float, notes: str) -> tuple[bool, str]:
    user = (st.session_state.get("finance_auth") or {}).get("user") or {}
    payload = {
        "user_id": user.get("id"),
        "tx_date": tx_date.isoformat(),
        "kind": kind,
        "status": status,
        "category": category.strip()[:80],
        "counterparty": counterparty.strip()[:120],
        "amount": round(float(amount), 2),
        "notes": notes.strip()[:500],
    }
    data, message = _db_request("POST", "finance_transactions", payload=payload, prefer="return=representation")
    return data is not None, message


def _login_screen() -> None:
    hero(
        "FINANZAS PRIVADAS",
        "Entiende tu negocio antes de abrir otra planilla.",
        "Tus ingresos, gastos, caja y pendientes en una sola vista. Cada cuenta ve únicamente su propia información.",
        "Acceso protegido con Supabase Auth",
    )
    left, center, right = st.columns([1, 1.15, 1])
    with center:
        tabs = st.tabs(["Ingresar", "Crear cuenta"])
        with tabs[0]:
            with st.form("finance_login"):
                email = st.text_input("Correo", placeholder="tu@empresa.cl")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Entrar a mi negocio", type="primary", width="stretch")
            if submit:
                if not email.strip() or not password:
                    st.error("Ingresa tu correo y contraseña.")
                else:
                    body, message = _auth_request("token?grant_type=password", {"email": email.strip().lower(), "password": password})
                    if body and _set_session(body):
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos." if "Invalid login" in message else message)

            with st.expander("¿Olvidaste tu contraseña?"):
                recover_email = st.text_input("Correo para recuperar acceso", key="recover_email")
                if st.button("Enviar correo de recuperación", width="stretch"):
                    if recover_email.strip():
                        _, message = _auth_request("recover", {"email": recover_email.strip().lower()})
                        if message == "ok":
                            st.success("Revisa tu correo. Si la cuenta existe, recibirás instrucciones.")
                        else:
                            st.error(message)

        with tabs[1]:
            with st.form("finance_signup"):
                name = st.text_input("Nombre", placeholder="Tu nombre")
                email = st.text_input("Correo", key="signup_email", placeholder="tu@empresa.cl")
                password = st.text_input("Contraseña", key="signup_password", type="password", help="Usa al menos 8 caracteres.")
                consent = st.checkbox("Acepto crear una cuenta para usar el módulo Finanzas.")
                submit = st.form_submit_button("Crear mi cuenta", type="primary", width="stretch")
            if submit:
                if len(name.strip()) < 2:
                    st.error("Escribe tu nombre.")
                elif "@" not in email or "." not in email:
                    st.error("Ingresa un correo válido.")
                elif len(password) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                elif not consent:
                    st.error("Necesitamos tu aceptación para crear la cuenta.")
                else:
                    body, message = _auth_request(
                        "signup",
                        {"email": email.strip().lower(), "password": password, "data": {"full_name": name.strip()[:120]}},
                    )
                    if body:
                        if _set_session(body):
                            st.rerun()
                        else:
                            st.success("Cuenta creada. Revisa tu correo para confirmar tu dirección y luego inicia sesión.")
                    else:
                        st.error(message)

        st.caption("No almacenamos tu contraseña en la aplicación. La autenticación la gestiona Supabase Auth.")


def _empty_onboarding(profile: dict | None) -> dict | None:
    if profile:
        return profile
    hero(
        "CONFIGURA TU NEGOCIO",
        "Primero necesitamos tres datos, no una implementación eterna.",
        "Con esto calcularemos caja y objetivos. Después puedes empezar a registrar movimientos.",
    )
    with st.form("finance_profile"):
        name = st.text_input("Nombre del negocio", placeholder="Ej. Servicios Andes SpA")
        initial_cash = st.number_input("Caja inicial", min_value=0.0, value=0.0, step=100000.0, format="%.0f")
        goal = st.number_input("Meta mensual de ingresos", min_value=0.0, value=5000000.0, step=250000.0, format="%.0f")
        submit = st.form_submit_button("Crear mi espacio financiero", type="primary", width="stretch")
    if submit:
        if len(name.strip()) < 2:
            st.error("Escribe el nombre del negocio.")
        else:
            ok, message = _save_profile(name, initial_cash, goal)
            if ok:
                st.success("Listo. Tu espacio financiero está creado.")
                st.rerun()
            else:
                st.error(message)
    return None


def _month_scope(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    now = pd.Timestamp.now()
    return df.loc[(df["tx_date"].dt.year == now.year) & (df["tx_date"].dt.month == now.month)].copy()


def _cash(profile: dict, df: pd.DataFrame) -> float:
    paid = df.loc[df["status"] == "pagado"] if not df.empty else df
    income = float(paid.loc[paid["kind"] == "ingreso", "amount"].sum()) if not paid.empty else 0.0
    expense = float(paid.loc[paid["kind"] == "gasto", "amount"].sum()) if not paid.empty else 0.0
    return float(profile.get("initial_cash") or 0) + income - expense


def _trend_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        monthly = pd.DataFrame({"Mes": [], "Ingresos": [], "Gastos": [], "Resultado": []})
    else:
        work = df.copy()
        work["month"] = work["tx_date"].dt.to_period("M").dt.to_timestamp()
        pivot = work.pivot_table(index="month", columns="kind", values="amount", aggfunc="sum", fill_value=0).reset_index()
        if "ingreso" not in pivot: pivot["ingreso"] = 0.0
        if "gasto" not in pivot: pivot["gasto"] = 0.0
        pivot["Resultado"] = pivot["ingreso"] - pivot["gasto"]
        pivot["Mes"] = pivot["month"].dt.strftime("%b %Y")
        monthly = pivot.rename(columns={"ingreso": "Ingresos", "gasto": "Gastos"}).tail(8)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly["Mes"], y=monthly["Ingresos"], name="Ingresos", marker_color="#2457F5", marker_line_width=0))
    fig.add_trace(go.Bar(x=monthly["Mes"], y=monthly["Gastos"], name="Gastos", marker_color="#D6DCE8", marker_line_width=0))
    fig.add_trace(go.Scatter(x=monthly["Mes"], y=monthly["Resultado"], name="Resultado", mode="lines+markers", line=dict(color="#12805C", width=3), marker=dict(size=7)))
    fig.update_layout(
        barmode="group", height=370, margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.08, x=0), hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#EEF1F5", zeroline=False, tickprefix="$", separatethousands=True),
    )
    return fig


def _category_chart(df: pd.DataFrame) -> go.Figure:
    expenses = df.loc[df["kind"] == "gasto"].copy() if not df.empty else df
    grouped = expenses.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=True).tail(7) if not expenses.empty else pd.DataFrame(columns=["category", "amount"])
    fig = go.Figure(go.Bar(x=grouped["amount"], y=grouped["category"], orientation="h", marker_color="#667085", marker_line_width=0))
    fig.update_layout(
        height=330, margin=dict(l=10, r=10, t=15, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis=dict(showgrid=True, gridcolor="#EEF1F5", tickprefix="$", separatethousands=True), yaxis=dict(showgrid=False),
    )
    return fig


def _new_transaction_panel() -> None:
    with st.expander("＋ Registrar movimiento", expanded=False):
        with st.form("new_finance_transaction", clear_on_submit=True):
            c1, c2 = st.columns(2)
            tx_date = c1.date_input("Fecha", value=date.today())
            kind_label = c2.selectbox("Tipo", ["Ingreso", "Gasto"])
            c3, c4 = st.columns(2)
            status_label = c3.selectbox("Estado", ["Pagado / cobrado", "Pendiente"])
            category = c4.text_input("Categoría", placeholder="Ej. Ventas, arriendo, proveedores")
            counterparty = st.text_input("Cliente / proveedor", placeholder="Opcional")
            amount = st.number_input("Monto", min_value=0.0, step=10000.0, format="%.0f")
            notes = st.text_input("Nota", placeholder="Opcional")
            submit = st.form_submit_button("Guardar movimiento", type="primary", width="stretch")
        if submit:
            if amount <= 0:
                st.error("El monto debe ser mayor a cero.")
            elif len(category.strip()) < 2:
                st.error("Indica una categoría.")
            else:
                ok, message = _add_transaction(
                    tx_date,
                    "ingreso" if kind_label == "Ingreso" else "gasto",
                    "pagado" if status_label == "Pagado / cobrado" else "pendiente",
                    category,
                    counterparty,
                    amount,
                    notes,
                )
                if ok:
                    st.success("Movimiento guardado.")
                    st.rerun()
                else:
                    st.error(message)


def _dashboard(profile: dict) -> None:
    auth = st.session_state.get("finance_auth") or {}
    user = auth.get("user") or {}
    df = _transactions()
    month = _month_scope(df)

    income = float(month.loc[month["kind"] == "ingreso", "amount"].sum()) if not month.empty else 0.0
    expense = float(month.loc[month["kind"] == "gasto", "amount"].sum()) if not month.empty else 0.0
    result = income - expense
    cash = _cash(profile, df)
    receivable = float(df.loc[(df["kind"] == "ingreso") & (df["status"] == "pendiente"), "amount"].sum()) if not df.empty else 0.0
    payable = float(df.loc[(df["kind"] == "gasto") & (df["status"] == "pendiente"), "amount"].sum()) if not df.empty else 0.0
    goal = float(profile.get("monthly_revenue_goal") or 0)
    goal_pct = income / goal if goal > 0 else 0

    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.markdown(f"<div class='hc-eyebrow'>FINANZAS · {profile.get('business_name','Mi negocio')}</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:2rem;font-weight:780;letter-spacing:-.04em;color:#101828;margin-bottom:4px'>Tu negocio, en números que llevan a una decisión.</div>", unsafe_allow_html=True)
        st.caption("Primero caja y resultado. Después el detalle.")
    with top_right:
        st.caption(user.get("email", ""))
        if st.button("Cerrar sesión", width="stretch"):
            _sign_out()

    _new_transaction_panel()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Caja disponible", _money(cash), "Incluye movimientos pagados")
    k2.metric("Ingresos del mes", _money(income), f"{goal_pct:.0%} de la meta" if goal else "Sin meta")
    k3.metric("Gastos del mes", _money(expense), f"{expense/income:.0%} de ingresos" if income else "Sin ingresos aún")
    k4.metric("Resultado del mes", _money(result), "Positivo" if result >= 0 else "Atención")

    if result < 0:
        st.markdown(f'<div class="hc-warning"><b>Atención al resultado.</b> Este mes los gastos superan los ingresos por {_money(abs(result))}. La siguiente decisión debería centrarse en caja y gastos controlables.</div>', unsafe_allow_html=True)
    elif income > 0:
        margin = result / income
        insight("Lectura ejecutiva", f"El mes lleva un resultado de {_money(result)} ({margin:.1%} sobre ingresos). Tienes {_money(receivable)} por cobrar y {_money(payable)} por pagar pendientes.")
    else:
        insight("Empieza por lo esencial", "Registra tus primeros ingresos y gastos. Con pocos movimientos ya podremos mostrar tendencia, caja y alertas útiles.")

    section("Movimiento del negocio", "Ingresos, gastos y resultado. La línea importa más que un gráfico lleno de indicadores.")
    st.plotly_chart(_trend_chart(df), width="stretch", config={"displayModeBar": False})

    left, right = st.columns([1.25, 1])
    with left:
        section("Pendientes que afectan caja")
        p1, p2 = st.columns(2)
        p1.metric("Por cobrar", _money(receivable), "Ingresos pendientes")
        p2.metric("Por pagar", _money(payable), "Gastos pendientes")
        if receivable > payable and receivable > 0:
            st.markdown('<div class="hc-positive"><b>Oportunidad de caja.</b> Cobrar pendientes tiene más impacto inmediato que recortar gastos pequeños.</div>', unsafe_allow_html=True)
        elif payable > 0:
            st.markdown('<div class="hc-warning"><b>Planifica pagos.</b> Revisa vencimientos y evita que los compromisos pendientes sorprendan a tu caja.</div>', unsafe_allow_html=True)
    with right:
        section("Dónde se concentra el gasto")
        if df.loc[df["kind"] == "gasto"].empty:
            st.info("Cuando registres gastos, aquí verás qué categorías concentran la salida de dinero.")
        else:
            st.plotly_chart(_category_chart(df), width="stretch", config={"displayModeBar": False})

    section("Últimos movimientos", "El detalle está abajo porque primero necesitas entender el negocio, no revisar filas.")
    if df.empty:
        st.info("Aún no hay movimientos. Usa “Registrar movimiento” para empezar.")
    else:
        view = df.head(20).copy()
        view["Fecha"] = view["tx_date"].dt.strftime("%d-%m-%Y")
        view["Tipo"] = view["kind"].map({"ingreso": "Ingreso", "gasto": "Gasto"})
        view["Estado"] = view["status"].map({"pagado": "Pagado / cobrado", "pendiente": "Pendiente"})
        view["Monto"] = view.apply(lambda r: _money(r["amount"]) if r["kind"] == "ingreso" else f"-{_money(r['amount'])}", axis=1)
        view = view.rename(columns={"category": "Categoría", "counterparty": "Cliente / proveedor", "notes": "Nota"})
        st.dataframe(view[["Fecha", "Tipo", "Estado", "Categoría", "Cliente / proveedor", "Monto", "Nota"]], hide_index=True, width="stretch")

    st.caption("Primera versión privada · datos separados por usuario mediante Row Level Security · todavía no reemplaza contabilidad ni asesoría tributaria.")


def render() -> None:
    if not st.session_state.get("finance_auth"):
        _login_screen()
        return
    profile = _empty_onboarding(_get_profile())
    if not profile:
        return
    _dashboard(profile)
