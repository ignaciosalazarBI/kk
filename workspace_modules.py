from __future__ import annotations

from datetime import date, timedelta
from io import StringIO

import pandas as pd
import streamlit as st

from design_system import insight, section
from finance_workspace import (
    _db_request,
    _empty_onboarding,
    _get_profile,
    _login_screen,
    _money,
)


def _guard() -> dict | None:
    if not st.session_state.get("finance_auth"):
        _login_screen()
        return None
    profile = _empty_onboarding(_get_profile())
    return profile


def _user_id() -> str:
    auth = st.session_state.get("finance_auth") or {}
    return str((auth.get("user") or {}).get("id") or "")


def _fetch(table: str, select: str = "*", order: str = "created_at.desc") -> list[dict]:
    params = {"select": select}
    if order:
        params["order"] = order
    data, _ = _db_request("GET", table, params=params)
    return list(data or []) if isinstance(data, list) else []


def _insert(table: str, payload: dict | list[dict]) -> tuple[bool, str]:
    data, message = _db_request("POST", table, payload=payload, prefer="return=representation")
    return data is not None, message


def _patch(table: str, row_id: str, payload: dict) -> tuple[bool, str]:
    data, message = _db_request(
        "PATCH",
        table,
        params={"id": f"eq.{row_id}"},
        payload=payload,
        prefer="return=representation",
    )
    return data is not None, message


def _delete(table: str, row_id: str) -> tuple[bool, str]:
    data, message = _db_request("DELETE", table, params={"id": f"eq.{row_id}"})
    return data is not None, message


def _frame(rows: list[dict], date_columns: tuple[str, ...] = ()) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hc-shell">
          <div class="hc-eyebrow">{kicker}</div>
          <div class="hc-hero-title">{title}</div>
          <div class="hc-hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _download_template(label: str, filename: str, columns: list[str], sample: dict) -> None:
    csv = pd.DataFrame([sample], columns=columns).to_csv(index=False)
    st.download_button(label, csv, filename, "text/csv", width="stretch")


def _read_csv(uploaded) -> pd.DataFrame:
    raw = uploaded.getvalue().decode("utf-8-sig", errors="replace")
    return pd.read_csv(StringIO(raw), sep=None, engine="python")


def render_collections() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header(
        "COBRANZA",
        "Cobra antes de que la caja se convierta en un problema.",
        "Registra facturas, vencimientos y pagos. Los datos quedan guardados únicamente en tu cuenta.",
    )
    rows = _fetch("collection_invoices", order="due_date.asc")
    df = _frame(rows, ("issue_date", "due_date"))
    today = pd.Timestamp.today().normalize()
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["paid_amount"] = pd.to_numeric(df["paid_amount"], errors="coerce").fillna(0.0)
        df["Saldo"] = (df["amount"] - df["paid_amount"]).clip(lower=0)
        df["Días"] = (today - df["due_date"]).dt.days
        open_mask = ~df["status"].isin(["pagada", "anulada"])
        receivable = float(df.loc[open_mask, "Saldo"].sum())
        overdue = float(df.loc[open_mask & (df["due_date"] < today), "Saldo"].sum())
        due_7 = float(df.loc[open_mask & (df["due_date"] >= today) & (df["due_date"] <= today + pd.Timedelta(days=7)), "Saldo"].sum())
        clients = int(df.loc[open_mask & (df["due_date"] < today), "customer"].nunique())
    else:
        receivable = overdue = due_7 = 0.0
        clients = 0

    a, b, c, d = st.columns(4)
    a.metric("Por cobrar", _money(receivable))
    b.metric("Vencido", _money(overdue))
    c.metric("Vence en 7 días", _money(due_7))
    d.metric("Clientes vencidos", clients)

    tabs = st.tabs(["Cartera", "Agregar factura", "Actualizar", "Importar CSV"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay facturas. Agrega una manualmente o importa tu cartera desde CSV.")
        else:
            view = df.copy()
            view["Emisión"] = view["issue_date"].dt.strftime("%d-%m-%Y")
            view["Vence"] = view["due_date"].dt.strftime("%d-%m-%Y")
            view["Monto"] = view["amount"].map(_money)
            view["Pagado"] = view["paid_amount"].map(_money)
            view["Saldo"] = view["Saldo"].map(_money)
            view["Estado"] = view["status"].str.replace("_", " ").str.title()
            st.dataframe(
                view[["customer", "document_no", "Emisión", "Vence", "Monto", "Pagado", "Saldo", "Estado"]].rename(
                    columns={"customer": "Cliente", "document_no": "Documento"}
                ),
                hide_index=True,
                width="stretch",
            )
            if overdue > 0:
                insight("Prioridad de hoy", f"Tienes {_money(overdue)} vencidos. Empieza por los documentos con mayor saldo y más días de atraso.")

    with tabs[1]:
        with st.form("add_collection_invoice", clear_on_submit=True):
            c1, c2 = st.columns(2)
            customer = c1.text_input("Cliente *")
            document = c2.text_input("N° documento")
            c3, c4 = st.columns(2)
            issue_date = c3.date_input("Fecha emisión", value=date.today())
            due_date = c4.date_input("Fecha vencimiento", value=date.today() + timedelta(days=30))
            amount = st.number_input("Monto", min_value=0.0, step=10000.0, format="%.0f")
            notes = st.text_input("Nota")
            submit = st.form_submit_button("Guardar factura", type="primary", width="stretch")
        if submit:
            if len(customer.strip()) < 2 or amount <= 0:
                st.error("Completa cliente y un monto mayor a cero.")
            else:
                ok, msg = _insert("collection_invoices", {
                    "user_id": _user_id(), "customer": customer.strip(), "document_no": document.strip(),
                    "issue_date": issue_date.isoformat(), "due_date": due_date.isoformat(), "amount": float(amount),
                    "paid_amount": 0, "status": "pendiente", "notes": notes.strip(),
                })
                if ok:
                    st.success("Factura guardada.")
                    st.rerun()
                else:
                    st.error(msg)

    with tabs[2]:
        if df.empty:
            st.info("No hay documentos para actualizar.")
        else:
            options = {f"{r['customer']} · {r.get('document_no','')} · {_money(float(r.get('amount',0)) - float(r.get('paid_amount',0)))}": r for r in rows}
            selected_label = st.selectbox("Documento", list(options))
            selected = options[selected_label]
            max_amount = float(selected.get("amount") or 0)
            paid_now = st.number_input("Total pagado acumulado", min_value=0.0, max_value=max_amount, value=float(selected.get("paid_amount") or 0), step=10000.0, format="%.0f")
            status = st.selectbox("Estado", ["pendiente", "parcial", "pagada", "vencida", "anulada"], index=["pendiente", "parcial", "pagada", "vencida", "anulada"].index(selected.get("status", "pendiente")))
            c1, c2 = st.columns(2)
            if c1.button("Guardar cambios", type="primary", width="stretch"):
                if paid_now >= max_amount and status not in ("anulada",):
                    status = "pagada"
                elif paid_now > 0 and status == "pendiente":
                    status = "parcial"
                ok, msg = _patch("collection_invoices", selected["id"], {"paid_amount": paid_now, "status": status, "updated_at": pd.Timestamp.utcnow().isoformat()})
                if ok:
                    st.success("Cobranza actualizada.")
                    st.rerun()
                else:
                    st.error(msg)
            if c2.button("Eliminar documento", width="stretch"):
                ok, msg = _delete("collection_invoices", selected["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)

    with tabs[3]:
        st.caption("Columnas: cliente, documento, fecha_emision, fecha_vencimiento, monto, pagado, notas")
        _download_template(
            "Descargar plantilla CSV", "cobranza_control_pyme.csv",
            ["cliente", "documento", "fecha_emision", "fecha_vencimiento", "monto", "pagado", "notas"],
            {"cliente": "Cliente Demo", "documento": "F-1001", "fecha_emision": "2026-08-01", "fecha_vencimiento": "2026-08-31", "monto": 850000, "pagado": 0, "notas": ""},
        )
        file = st.file_uploader("Subir CSV de cobranza", type=["csv"], key="collections_csv")
        if file and st.button("Importar cobranza", type="primary", width="stretch"):
            try:
                imp = _read_csv(file)
                required = {"cliente", "fecha_vencimiento", "monto"}
                if not required.issubset(set(imp.columns)):
                    raise ValueError("Faltan columnas obligatorias: cliente, fecha_vencimiento, monto")
                payload = []
                for _, r in imp.iterrows():
                    amount = float(r.get("monto") or 0)
                    paid = float(r.get("pagado") or 0)
                    if amount <= 0 or not str(r.get("cliente") or "").strip():
                        continue
                    payload.append({
                        "user_id": _user_id(), "customer": str(r.get("cliente")).strip()[:160],
                        "document_no": str(r.get("documento") or "").strip()[:80],
                        "issue_date": pd.to_datetime(r.get("fecha_emision"), errors="coerce").date().isoformat() if pd.notna(pd.to_datetime(r.get("fecha_emision"), errors="coerce")) else date.today().isoformat(),
                        "due_date": pd.to_datetime(r.get("fecha_vencimiento"), errors="raise").date().isoformat(),
                        "amount": amount, "paid_amount": max(0, min(paid, amount)),
                        "status": "pagada" if paid >= amount else ("parcial" if paid > 0 else "pendiente"),
                        "notes": str(r.get("notas") or "")[:500],
                    })
                ok, msg = _insert("collection_invoices", payload)
                if not payload:
                    st.warning("No encontramos filas válidas para importar.")
                elif ok:
                    st.success(f"Importadas {len(payload)} facturas.")
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as exc:
                st.error(f"No pudimos importar el CSV: {exc}")


def render_inventory() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("INVENTARIO", "Stock que se entiende antes de comprar de más.", "Controla existencias, mínimos, costo, precio y alertas de reposición con datos reales de tu negocio.")
    rows = _fetch("inventory_items", order="name.asc")
    df = _frame(rows)
    if not df.empty:
        for col in ("stock_qty", "min_stock", "unit_cost", "unit_price"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        df["Valor stock"] = df["stock_qty"] * df["unit_cost"]
        df["Venta potencial"] = df["stock_qty"] * df["unit_price"]
        df["Bajo mínimo"] = df["stock_qty"] <= df["min_stock"]
        stock_value = float(df["Valor stock"].sum())
        low = int(df["Bajo mínimo"].sum())
        units = float(df["stock_qty"].sum())
        potential = float(df["Venta potencial"].sum())
    else:
        stock_value = potential = units = 0.0
        low = 0
    a, b, c, d = st.columns(4)
    a.metric("Valor de stock", _money(stock_value))
    b.metric("Productos bajo mínimo", low)
    c.metric("Unidades", f"{units:,.0f}".replace(",", "."))
    d.metric("Venta potencial", _money(potential))
    tabs = st.tabs(["Stock", "Agregar producto", "Ajustar stock", "Importar CSV"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay productos cargados.")
        else:
            view = df.copy()
            view["Costo"] = view["unit_cost"].map(_money)
            view["Precio"] = view["unit_price"].map(_money)
            view["Valor"] = view["Valor stock"].map(_money)
            view["Alerta"] = view["Bajo mínimo"].map({True: "Reponer", False: "OK"})
            st.dataframe(view[["sku", "name", "category", "stock_qty", "min_stock", "Costo", "Precio", "Valor", "Alerta"]].rename(columns={"sku": "SKU", "name": "Producto", "category": "Categoría", "stock_qty": "Stock", "min_stock": "Mínimo"}), hide_index=True, width="stretch")
    with tabs[1]:
        with st.form("add_inventory_item", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sku = c1.text_input("SKU")
            name = c2.text_input("Producto *")
            category = st.text_input("Categoría", value="General")
            c3, c4 = st.columns(2)
            stock = c3.number_input("Stock actual", value=0.0, step=1.0)
            minimum = c4.number_input("Stock mínimo", min_value=0.0, value=0.0, step=1.0)
            c5, c6 = st.columns(2)
            cost = c5.number_input("Costo unitario", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
            price = c6.number_input("Precio unitario", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
            submit = st.form_submit_button("Guardar producto", type="primary", width="stretch")
        if submit:
            if len(name.strip()) < 2:
                st.error("Escribe el nombre del producto.")
            else:
                ok, msg = _insert("inventory_items", {"user_id": _user_id(), "sku": sku.strip(), "name": name.strip(), "category": category.strip() or "General", "stock_qty": stock, "min_stock": minimum, "unit_cost": cost, "unit_price": price})
                if ok:
                    st.rerun()
                else:
                    st.error("Ese SKU ya existe o los datos no son válidos." if "duplicate" in msg.lower() else msg)
    with tabs[2]:
        if df.empty:
            st.info("No hay productos para ajustar.")
        else:
            options = {f"{r.get('sku','')} · {r['name']} · stock {r.get('stock_qty',0)}": r for r in rows}
            label = st.selectbox("Producto", list(options))
            row = options[label]
            new_stock = st.number_input("Nuevo stock", value=float(row.get("stock_qty") or 0), step=1.0)
            c1, c2 = st.columns(2)
            if c1.button("Actualizar stock", type="primary", width="stretch"):
                ok, msg = _patch("inventory_items", row["id"], {"stock_qty": new_stock, "updated_at": pd.Timestamp.utcnow().isoformat()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
            if c2.button("Eliminar producto", width="stretch"):
                ok, msg = _delete("inventory_items", row["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
    with tabs[3]:
        st.caption("Columnas: sku, producto, categoria, stock, minimo, costo, precio")
        _download_template("Descargar plantilla CSV", "inventario_control_pyme.csv", ["sku", "producto", "categoria", "stock", "minimo", "costo", "precio"], {"sku": "SKU-001", "producto": "Producto Demo", "categoria": "General", "stock": 20, "minimo": 5, "costo": 10000, "precio": 18000})
        file = st.file_uploader("Subir CSV de inventario", type=["csv"], key="inventory_csv")
        if file and st.button("Importar inventario", type="primary", width="stretch"):
            try:
                imp = _read_csv(file)
                if not {"producto", "stock"}.issubset(imp.columns):
                    raise ValueError("Faltan columnas producto y stock")
                payload = []
                for _, r in imp.iterrows():
                    name = str(r.get("producto") or "").strip()
                    if not name:
                        continue
                    payload.append({"user_id": _user_id(), "sku": str(r.get("sku") or "").strip()[:80], "name": name[:160], "category": str(r.get("categoria") or "General")[:100], "stock_qty": float(r.get("stock") or 0), "min_stock": max(0, float(r.get("minimo") or 0)), "unit_cost": max(0, float(r.get("costo") or 0)), "unit_price": max(0, float(r.get("precio") or 0))})
                ok, msg = _insert("inventory_items", payload)
                if ok and payload:
                    st.success(f"Importados {len(payload)} productos.")
                    st.rerun()
                elif not payload:
                    st.warning("No encontramos filas válidas.")
                else:
                    st.error(msg)
            except Exception as exc:
                st.error(f"No pudimos importar: {exc}")


def render_bank() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("CONCILIACIÓN BANCARIA", "La cartola entra; tú revisas solo las excepciones.", "Carga movimientos bancarios reales por CSV o regístralos manualmente. No necesitamos tu clave bancaria.")
    rows = _fetch("bank_transactions", order="tx_date.desc")
    df = _frame(rows, ("tx_date",))
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        pending_mask = df["status"] == "pendiente"
        pending_count = int(pending_mask.sum())
        pending_amount = float(df.loc[pending_mask, "amount"].sum())
        reconciled = int((df["status"] == "conciliado").sum())
        rate = reconciled / len(df) if len(df) else 0
    else:
        pending_count = reconciled = 0
        pending_amount = rate = 0.0
    a, b, c = st.columns(3)
    a.metric("Pendientes", pending_count)
    b.metric("Monto por revisar", _money(pending_amount))
    c.metric("Conciliado", f"{rate:.0%}")
    tabs = st.tabs(["Movimientos", "Agregar", "Conciliar", "Importar CSV"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay movimientos bancarios.")
        else:
            view = df.copy()
            view["Fecha"] = view["tx_date"].dt.strftime("%d-%m-%Y")
            view["Monto"] = view["amount"].map(_money)
            view["Tipo"] = view["direction"].map({"ingreso": "Ingreso", "egreso": "Egreso"})
            view["Estado"] = view["status"].str.title()
            st.dataframe(view[["Fecha", "description", "Tipo", "Monto", "reference", "Estado"]].rename(columns={"description": "Descripción", "reference": "Referencia"}), hide_index=True, width="stretch")
    with tabs[1]:
        with st.form("add_bank_tx", clear_on_submit=True):
            c1, c2 = st.columns(2)
            tx_date = c1.date_input("Fecha", value=date.today(), key="bank_date")
            direction = c2.selectbox("Tipo", ["Ingreso", "Egreso"])
            description = st.text_input("Descripción *")
            amount = st.number_input("Monto", min_value=0.0, step=10000.0, format="%.0f", key="bank_amount")
            reference = st.text_input("Referencia")
            submit = st.form_submit_button("Guardar movimiento", type="primary", width="stretch")
        if submit:
            if len(description.strip()) < 2 or amount <= 0:
                st.error("Completa descripción y monto.")
            else:
                ok, msg = _insert("bank_transactions", {"user_id": _user_id(), "tx_date": tx_date.isoformat(), "description": description.strip(), "amount": amount, "direction": direction.lower(), "status": "pendiente", "reference": reference.strip()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
    with tabs[2]:
        pending_rows = [r for r in rows if r.get("status") == "pendiente"]
        finance = _fetch("finance_transactions", select="id,tx_date,kind,status,category,counterparty,amount,notes", order="tx_date.desc")
        if not pending_rows:
            st.success("No tienes movimientos pendientes de conciliación.")
        else:
            bank_opts = {f"{r.get('tx_date')} · {r.get('description')} · {_money(float(r.get('amount') or 0))}": r for r in pending_rows}
            bank_label = st.selectbox("Movimiento bancario", list(bank_opts))
            bank_row = bank_opts[bank_label]
            if finance:
                fin_opts = {f"{r.get('tx_date')} · {r.get('counterparty') or r.get('category')} · {_money(float(r.get('amount') or 0))}": r for r in finance}
                fin_label = st.selectbox("Movimiento financiero relacionado", list(fin_opts))
                fin_row = fin_opts[fin_label]
                if st.button("Marcar como conciliado", type="primary", width="stretch"):
                    ok, msg = _patch("bank_transactions", bank_row["id"], {"status": "conciliado", "matched_finance_transaction_id": fin_row["id"], "updated_at": pd.Timestamp.utcnow().isoformat()})
                    if ok:
                        st.success("Movimiento conciliado.")
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Registra movimientos en Finanzas para poder vincularlos. También puedes ignorar movimientos que no correspondan al negocio.")
                if st.button("Ignorar este movimiento", width="stretch"):
                    ok, msg = _patch("bank_transactions", bank_row["id"], {"status": "ignorado", "updated_at": pd.Timestamp.utcnow().isoformat()})
                    if ok:
                        st.rerun()
                    else:
                        st.error(msg)
    with tabs[3]:
        st.caption("Columnas: fecha, descripcion, monto, tipo, referencia. Tipo debe ser ingreso o egreso.")
        _download_template("Descargar plantilla CSV", "cartola_control_pyme.csv", ["fecha", "descripcion", "monto", "tipo", "referencia"], {"fecha": "2026-08-29", "descripcion": "Transferencia cliente", "monto": 550000, "tipo": "ingreso", "referencia": "TRX-001"})
        file = st.file_uploader("Subir cartola CSV", type=["csv"], key="bank_csv")
        if file and st.button("Importar cartola", type="primary", width="stretch"):
            try:
                imp = _read_csv(file)
                if not {"fecha", "descripcion", "monto"}.issubset(imp.columns):
                    raise ValueError("Faltan fecha, descripcion o monto")
                payload = []
                for _, r in imp.iterrows():
                    amount_raw = float(r.get("monto") or 0)
                    direction = str(r.get("tipo") or ("ingreso" if amount_raw >= 0 else "egreso")).strip().lower()
                    direction = direction if direction in ("ingreso", "egreso") else ("ingreso" if amount_raw >= 0 else "egreso")
                    payload.append({"user_id": _user_id(), "tx_date": pd.to_datetime(r.get("fecha"), errors="raise").date().isoformat(), "description": str(r.get("descripcion") or "Movimiento")[:220], "amount": abs(amount_raw), "direction": direction, "status": "pendiente", "reference": str(r.get("referencia") or "")[:120]})
                ok, msg = _insert("bank_transactions", payload)
                if ok and payload:
                    st.success(f"Importados {len(payload)} movimientos.")
                    st.rerun()
                else:
                    st.error(msg if payload else "No encontramos filas válidas.")
            except Exception as exc:
                st.error(f"No pudimos importar la cartola: {exc}")


def render_marketing() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("MARKETING", "Mide ventas, no likes.", "Registra campañas y compara inversión, leads, ventas e ingresos para decidir dónde poner el próximo peso.")
    rows = _fetch("marketing_campaigns", order="start_date.desc")
    df = _frame(rows, ("start_date", "end_date"))
    if not df.empty:
        for col in ("budget", "spend", "revenue"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        df["leads"] = pd.to_numeric(df["leads"], errors="coerce").fillna(0)
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)
        spend = float(df["spend"].sum())
        revenue = float(df["revenue"].sum())
        leads = int(df["leads"].sum())
        sales = int(df["sales"].sum())
        roas = revenue / spend if spend > 0 else 0
        cpl = spend / leads if leads > 0 else 0
    else:
        spend = revenue = roas = cpl = 0.0
        leads = sales = 0
    a, b, c, d = st.columns(4)
    a.metric("Inversión", _money(spend))
    b.metric("Ingresos atribuidos", _money(revenue))
    c.metric("ROAS", f"{roas:.2f}x")
    d.metric("Costo por lead", _money(cpl))
    tabs = st.tabs(["Campañas", "Nueva campaña", "Administrar"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay campañas.")
        else:
            view = df.copy()
            view["Inversión"] = view["spend"].map(_money)
            view["Ingresos"] = view["revenue"].map(_money)
            view["ROAS"] = view.apply(lambda r: f"{(r['revenue']/r['spend']):.2f}x" if r["spend"] > 0 else "—", axis=1)
            st.dataframe(view[["name", "channel", "status", "Inversión", "leads", "sales", "Ingresos", "ROAS"]].rename(columns={"name": "Campaña", "channel": "Canal", "status": "Estado", "leads": "Leads", "sales": "Ventas"}), hide_index=True, width="stretch")
            if spend > 0:
                insight("Lectura comercial", f"Por cada $1 invertido, las campañas registradas están generando aproximadamente ${roas:.2f} en ingresos atribuidos.")
    with tabs[1]:
        with st.form("add_campaign", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Campaña *")
            channel = c2.selectbox("Canal", ["Meta Ads", "Google Ads", "LinkedIn", "Email", "Orgánico", "Referidos", "Otro"])
            c3, c4 = st.columns(2)
            start_date = c3.date_input("Inicio", value=date.today())
            end_date = c4.date_input("Término", value=date.today() + timedelta(days=30))
            c5, c6 = st.columns(2)
            budget = c5.number_input("Presupuesto", min_value=0.0, step=10000.0, format="%.0f")
            spend_value = c6.number_input("Gasto real", min_value=0.0, step=10000.0, format="%.0f")
            c7, c8, c9 = st.columns(3)
            leads_value = c7.number_input("Leads", min_value=0, step=1)
            sales_value = c8.number_input("Ventas", min_value=0, step=1)
            revenue_value = c9.number_input("Ingresos", min_value=0.0, step=10000.0, format="%.0f")
            status = st.selectbox("Estado", ["planificada", "activa", "pausada", "finalizada"])
            notes = st.text_input("Nota")
            submit = st.form_submit_button("Guardar campaña", type="primary", width="stretch")
        if submit:
            if len(name.strip()) < 2:
                st.error("Escribe el nombre de la campaña.")
            else:
                ok, msg = _insert("marketing_campaigns", {"user_id": _user_id(), "name": name.strip(), "channel": channel, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "budget": budget, "spend": spend_value, "leads": leads_value, "sales": sales_value, "revenue": revenue_value, "status": status, "notes": notes.strip()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
    with tabs[2]:
        if not rows:
            st.info("No hay campañas para administrar.")
        else:
            options = {f"{r['name']} · {r['channel']}": r for r in rows}
            label = st.selectbox("Campaña", list(options))
            row = options[label]
            status = st.selectbox("Nuevo estado", ["planificada", "activa", "pausada", "finalizada"], index=["planificada", "activa", "pausada", "finalizada"].index(row.get("status", "activa")))
            c1, c2 = st.columns(2)
            if c1.button("Actualizar estado", type="primary", width="stretch"):
                ok, msg = _patch("marketing_campaigns", row["id"], {"status": status, "updated_at": pd.Timestamp.utcnow().isoformat()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
            if c2.button("Eliminar campaña", width="stretch"):
                ok, msg = _delete("marketing_campaigns", row["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)


def render_legal() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("LEGAL", "Fechas críticas visibles antes de que se vuelvan urgencias.", "Registra contratos, renovaciones, montos y vencimientos. No subas documentos sensibles todavía; esta versión guarda metadatos del contrato.")
    rows = _fetch("legal_contracts", order="renewal_date.asc")
    df = _frame(rows, ("start_date", "end_date", "renewal_date"))
    today = pd.Timestamp.today().normalize()
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        active = int(df["status"].isin(["vigente", "por_vencer"]).sum())
        expiring = int(((df["renewal_date"].notna()) & (df["renewal_date"] >= today) & (df["renewal_date"] <= today + pd.Timedelta(days=30))).sum())
        expired = int(((df["end_date"].notna()) & (df["end_date"] < today) & ~df["status"].isin(["terminado"])).sum())
        value = float(df.loc[df["status"].isin(["vigente", "por_vencer"]), "amount"].sum())
    else:
        active = expiring = expired = 0
        value = 0.0
    a, b, c, d = st.columns(4)
    a.metric("Contratos vigentes", active)
    b.metric("Renuevan en 30 días", expiring)
    c.metric("Vencidos por revisar", expired)
    d.metric("Valor registrado", _money(value))
    tabs = st.tabs(["Contratos", "Nuevo contrato", "Administrar"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay contratos registrados.")
        else:
            view = df.copy()
            view["Término"] = view["end_date"].dt.strftime("%d-%m-%Y")
            view["Renovación"] = view["renewal_date"].dt.strftime("%d-%m-%Y")
            view["Monto"] = view["amount"].map(_money)
            st.dataframe(view[["name", "counterparty", "contract_type", "status", "Término", "Renovación", "Monto"]].rename(columns={"name": "Contrato", "counterparty": "Contraparte", "contract_type": "Tipo", "status": "Estado"}), hide_index=True, width="stretch")
    with tabs[1]:
        with st.form("add_contract", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Contrato *")
            counterparty = c2.text_input("Contraparte")
            contract_type = st.selectbox("Tipo", ["Cliente", "Proveedor", "Arriendo", "Laboral", "Servicio", "Licencia", "Otro"])
            c3, c4, c5 = st.columns(3)
            start_date = c3.date_input("Inicio", value=date.today())
            end_date = c4.date_input("Término", value=date.today() + timedelta(days=365))
            renewal_date = c5.date_input("Renovación / aviso", value=date.today() + timedelta(days=335))
            amount = st.number_input("Monto asociado", min_value=0.0, step=10000.0, format="%.0f")
            status = st.selectbox("Estado", ["borrador", "vigente", "por_vencer", "vencido", "terminado"], index=1)
            notes = st.text_input("Nota")
            submit = st.form_submit_button("Guardar contrato", type="primary", width="stretch")
        if submit:
            if len(name.strip()) < 2:
                st.error("Escribe el nombre del contrato.")
            else:
                ok, msg = _insert("legal_contracts", {"user_id": _user_id(), "name": name.strip(), "counterparty": counterparty.strip(), "contract_type": contract_type, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "renewal_date": renewal_date.isoformat(), "amount": amount, "status": status, "notes": notes.strip()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
    with tabs[2]:
        if not rows:
            st.info("No hay contratos para administrar.")
        else:
            options = {f"{r['name']} · {r.get('counterparty','')}": r for r in rows}
            label = st.selectbox("Contrato", list(options))
            row = options[label]
            status = st.selectbox("Nuevo estado", ["borrador", "vigente", "por_vencer", "vencido", "terminado"], index=["borrador", "vigente", "por_vencer", "vencido", "terminado"].index(row.get("status", "vigente")))
            c1, c2 = st.columns(2)
            if c1.button("Actualizar contrato", type="primary", width="stretch"):
                ok, msg = _patch("legal_contracts", row["id"], {"status": status, "updated_at": pd.Timestamp.utcnow().isoformat()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
            if c2.button("Eliminar contrato", width="stretch"):
                ok, msg = _delete("legal_contracts", row["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)


def render_tax() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("SII / IMPUESTOS", "Tus obligaciones ordenadas sin compartir la clave del SII.", "Registra F29, IVA, PPM, renta u otras obligaciones y controla vencimientos. La conexión automática al SII requerirá una integración oficial posterior.")
    rows = _fetch("tax_obligations", order="due_date.asc")
    df = _frame(rows, ("due_date",))
    today = pd.Timestamp.today().normalize()
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        open_mask = ~df["status"].isin(["pagada", "presentada", "no_aplica"])
        overdue = int((open_mask & (df["due_date"] < today)).sum())
        due_30 = int((open_mask & (df["due_date"] >= today) & (df["due_date"] <= today + pd.Timedelta(days=30))).sum())
        amount_open = float(df.loc[open_mask, "amount"].sum())
        completed = int(df["status"].isin(["pagada", "presentada"]).sum())
    else:
        overdue = due_30 = completed = 0
        amount_open = 0.0
    a, b, c, d = st.columns(4)
    a.metric("Vencidas", overdue)
    b.metric("Vencen en 30 días", due_30)
    c.metric("Monto pendiente", _money(amount_open))
    d.metric("Cumplidas", completed)
    tabs = st.tabs(["Calendario tributario", "Nueva obligación", "Actualizar"])
    with tabs[0]:
        if df.empty:
            st.info("Aún no hay obligaciones registradas.")
        else:
            view = df.copy()
            view["Vence"] = view["due_date"].dt.strftime("%d-%m-%Y")
            view["Monto"] = view["amount"].map(_money)
            st.dataframe(view[["period", "obligation_type", "Vence", "Monto", "status", "notes"]].rename(columns={"period": "Periodo", "obligation_type": "Obligación", "status": "Estado", "notes": "Nota"}), hide_index=True, width="stretch")
    with tabs[1]:
        with st.form("add_tax", clear_on_submit=True):
            c1, c2 = st.columns(2)
            period = c1.text_input("Periodo", placeholder="2026-08")
            obligation = c2.selectbox("Obligación", ["F29 / IVA", "PPM", "F22 / Renta", "Retenciones", "DJ", "Patente", "Otra"])
            due = st.date_input("Fecha vencimiento", value=date.today() + timedelta(days=10))
            amount = st.number_input("Monto estimado / pagado", min_value=0.0, step=10000.0, format="%.0f")
            status = st.selectbox("Estado", ["pendiente", "presentada", "pagada", "vencida", "no_aplica"])
            notes = st.text_input("Nota")
            submit = st.form_submit_button("Guardar obligación", type="primary", width="stretch")
        if submit:
            ok, msg = _insert("tax_obligations", {"user_id": _user_id(), "period": period.strip(), "obligation_type": obligation, "due_date": due.isoformat(), "amount": amount, "status": status, "notes": notes.strip()})
            if ok:
                st.rerun()
            else:
                st.error(msg)
    with tabs[2]:
        if not rows:
            st.info("No hay obligaciones para actualizar.")
        else:
            options = {f"{r.get('period','')} · {r['obligation_type']} · {r['due_date']}": r for r in rows}
            label = st.selectbox("Obligación", list(options))
            row = options[label]
            status = st.selectbox("Nuevo estado", ["pendiente", "presentada", "pagada", "vencida", "no_aplica"], index=["pendiente", "presentada", "pagada", "vencida", "no_aplica"].index(row.get("status", "pendiente")))
            c1, c2 = st.columns(2)
            if c1.button("Actualizar estado", type="primary", width="stretch"):
                ok, msg = _patch("tax_obligations", row["id"], {"status": status, "updated_at": pd.Timestamp.utcnow().isoformat()})
                if ok:
                    st.rerun()
                else:
                    st.error(msg)
            if c2.button("Eliminar obligación", width="stretch"):
                ok, msg = _delete("tax_obligations", row["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)


def render_ai() -> None:
    profile = _guard()
    if not profile:
        return
    _page_header("ASISTENTE IA", "Una lista corta de decisiones, no ocho dashboards para revisar.", "Esta primera versión cruza automáticamente tus datos reales y prioriza señales financieras, operativas y de cumplimiento.")
    finance = _frame(_fetch("finance_transactions", select="id,tx_date,kind,status,category,counterparty,amount,notes", order="tx_date.desc"), ("tx_date",))
    collections = _frame(_fetch("collection_invoices", order="due_date.asc"), ("due_date",))
    inventory = _frame(_fetch("inventory_items", order="name.asc"))
    bank = _frame(_fetch("bank_transactions", order="tx_date.desc"), ("tx_date",))
    marketing = _frame(_fetch("marketing_campaigns", order="start_date.desc"))
    legal = _frame(_fetch("legal_contracts", order="renewal_date.asc"), ("renewal_date", "end_date"))
    tax = _frame(_fetch("tax_obligations", order="due_date.asc"), ("due_date",))
    today = pd.Timestamp.today().normalize()

    actions: list[tuple[int, str, str]] = []
    score = 100

    if not collections.empty:
        collections["amount"] = pd.to_numeric(collections["amount"], errors="coerce").fillna(0.0)
        collections["paid_amount"] = pd.to_numeric(collections["paid_amount"], errors="coerce").fillna(0.0)
        open_mask = ~collections["status"].isin(["pagada", "anulada"])
        overdue_mask = open_mask & (collections["due_date"] < today)
        overdue = float((collections.loc[overdue_mask, "amount"] - collections.loc[overdue_mask, "paid_amount"]).clip(lower=0).sum())
        if overdue > 0:
            actions.append((1, "Cobranza", f"Gestiona {_money(overdue)} vencidos. Es la acción con impacto más inmediato sobre caja."))
            score -= 18

    if not bank.empty:
        bank["amount"] = pd.to_numeric(bank["amount"], errors="coerce").fillna(0.0)
        pending_bank = bank["status"] == "pendiente"
        if pending_bank.any():
            amount = float(bank.loc[pending_bank, "amount"].sum())
            actions.append((2, "Conciliación", f"Tienes {int(pending_bank.sum())} movimientos por conciliar por {_money(amount)}."))
            score -= min(12, int(pending_bank.sum()) * 2)

    if not inventory.empty:
        inventory["stock_qty"] = pd.to_numeric(inventory["stock_qty"], errors="coerce").fillna(0.0)
        inventory["min_stock"] = pd.to_numeric(inventory["min_stock"], errors="coerce").fillna(0.0)
        low = inventory["stock_qty"] <= inventory["min_stock"]
        if low.any():
            names = ", ".join(inventory.loc[low, "name"].astype(str).head(3).tolist())
            actions.append((3, "Inventario", f"{int(low.sum())} productos están bajo mínimo. Revisa primero: {names}."))
            score -= min(10, int(low.sum()) * 2)

    if not tax.empty:
        tax_open = ~tax["status"].isin(["pagada", "presentada", "no_aplica"])
        overdue_tax = tax_open & (tax["due_date"] < today)
        if overdue_tax.any():
            actions.append((1, "SII", f"Tienes {int(overdue_tax.sum())} obligaciones tributarias vencidas registradas. Revísalas hoy."))
            score -= 20

    if not legal.empty:
        renew = legal["renewal_date"].notna() & (legal["renewal_date"] >= today) & (legal["renewal_date"] <= today + pd.Timedelta(days=30))
        if renew.any():
            actions.append((2, "Legal", f"{int(renew.sum())} contratos requieren revisión o renovación dentro de 30 días."))
            score -= min(10, int(renew.sum()) * 3)

    if not marketing.empty:
        for col in ("spend", "revenue"):
            marketing[col] = pd.to_numeric(marketing[col], errors="coerce").fillna(0.0)
        spend = float(marketing["spend"].sum())
        revenue = float(marketing["revenue"].sum())
        if spend > 0:
            roas = revenue / spend
            if roas < 1:
                actions.append((3, "Marketing", f"El ROAS acumulado es {roas:.2f}x. Revisa campañas antes de aumentar presupuesto."))
                score -= 10
            elif roas >= 3:
                actions.append((5, "Marketing", f"El ROAS acumulado es {roas:.2f}x. Identifica la campaña ganadora antes de escalar inversión."))

    if not finance.empty:
        finance["amount"] = pd.to_numeric(finance["amount"], errors="coerce").fillna(0.0)
        month = finance.loc[(finance["tx_date"].dt.year == today.year) & (finance["tx_date"].dt.month == today.month)]
        income = float(month.loc[month["kind"] == "ingreso", "amount"].sum()) if not month.empty else 0.0
        expense = float(month.loc[month["kind"] == "gasto", "amount"].sum()) if not month.empty else 0.0
        if expense > income and expense > 0:
            actions.append((1, "Finanzas", f"Este mes los gastos superan los ingresos por {_money(expense - income)}."))
            score -= 18

    score = max(0, min(100, score))
    a, b, c = st.columns(3)
    a.metric("Salud operativa", f"{score}/100")
    b.metric("Acciones detectadas", len(actions))
    sources = sum(not x.empty for x in [finance, collections, inventory, bank, marketing, legal, tax])
    c.metric("Módulos con datos", f"{sources}/7")

    section("Qué haría hoy", "Ordenado por impacto y urgencia a partir de la información que ya registraste.")
    if not actions:
        st.success("No detectamos alertas críticas con los datos actuales. Sigue cargando información para mejorar la lectura.")
    else:
        for priority, area, text in sorted(actions, key=lambda x: x[0]):
            badge = "Alta" if priority == 1 else ("Media" if priority <= 3 else "Oportunidad")
            st.markdown(f"**{area} · {badge}**  \n{text}")
            st.divider()
    st.caption("Motor inteligente v1: recomendaciones automáticas basadas en reglas sobre tus datos. No sustituye asesoría contable, tributaria o legal. Más adelante puede incorporarse un modelo generativo con controles de privacidad.")


RENDERERS = {
    "cobranza": render_collections,
    "sii": render_tax,
    "marketing": render_marketing,
    "inventario": render_inventory,
    "conciliacion": render_bank,
    "legal": render_legal,
    "ia": render_ai,
}
