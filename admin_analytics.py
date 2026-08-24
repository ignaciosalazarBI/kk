from __future__ import annotations

import pandas as pd

MODULE_PAGE_EVENTS = {
    "Finanzas": "pantalla_finanzas",
    "Cobranza": "pantalla_cobranza",
    "SII": "pantalla_sii",
    "Marketing": "pantalla_marketing",
    "Inventario": "pantalla_inventario",
    "Conciliación bancaria": "pantalla_conciliacion_bancaria",
    "Legal": "pantalla_legal",
    "IA": "pantalla_ia",
}
MODULE_INTEREST_EVENTS = {
    "Finanzas": "modulo_finanzas",
    "Cobranza": "modulo_cobranza",
    "SII": "modulo_sii",
    "Marketing": "modulo_marketing",
    "Inventario": "modulo_inventario",
    "Conciliación bancaria": "modulo_conciliacion_bancaria",
    "Legal": "modulo_legal",
    "IA": "modulo_ia",
}
MODULE_PRIORITY_EVENTS = {
    module: event.replace("modulo_", "modulo_prioridad_", 1)
    for module, event in MODULE_INTEREST_EVENTS.items()
}
MODULE_EVENT_TO_NAME = {event: module for module, event in MODULE_PAGE_EVENTS.items()}
MODULE_PAGE_EVENT_SET = set(MODULE_PAGE_EVENTS.values())


def normalize_tracking(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    for name, default in [
        ("utm_source", "direct"),
        ("utm_medium", "none"),
        ("utm_campaign", "beta_publica"),
    ]:
        if name not in out.columns:
            out[name] = default
        out[name] = out[name].fillna(default).astype(str).str.strip().replace("", default)
    return out


def filter_since(df: pd.DataFrame, start: pd.Timestamp | None) -> pd.DataFrame:
    if df.empty or start is None or "created_at" not in df.columns:
        return df.copy()
    return df.loc[df["created_at"].notna() & (df["created_at"] >= start)].copy()


def filter_tracking(df: pd.DataFrame, channel: str, campaign: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    if channel != "Todos" and "utm_source" in out.columns:
        out = out.loc[out["utm_source"] == channel]
    if campaign != "Todas" and "utm_campaign" in out.columns:
        out = out.loc[out["utm_campaign"] == campaign]
    return out.copy()


def event_sessions(events: pd.DataFrame, event_name: str) -> int:
    if events.empty or "evento" not in events.columns or "session_id" not in events.columns:
        return 0
    return int(events.loc[events["evento"] == event_name, "session_id"].nunique())


def visit_cohort(events: pd.DataFrame) -> pd.DataFrame:
    """Keep only sessions that have a visit event inside the current filtered period."""
    if events.empty or not {"evento", "session_id"}.issubset(events.columns):
        return events.iloc[0:0].copy()
    visit_ids = events.loc[events["evento"] == "visita", "session_id"].dropna().unique()
    if len(visit_ids) == 0:
        return events.iloc[0:0].copy()
    return events.loc[events["session_id"].isin(visit_ids)].copy()


def module_explorers(events: pd.DataFrame) -> int:
    if events.empty or "evento" not in events.columns or "session_id" not in events.columns:
        return 0
    return int(events.loc[events["evento"].isin(MODULE_PAGE_EVENT_SET), "session_id"].nunique())


def pct(value: int | float, total: int | float) -> str:
    return f"{value / total * 100:.1f}%" if total else "—"


def build_module_table(events: pd.DataFrame, visits: int) -> pd.DataFrame:
    first_counts: dict[str, int] = {}
    if not events.empty and {"evento", "session_id", "created_at"}.issubset(events.columns):
        pages = events.loc[events["evento"].isin(MODULE_PAGE_EVENT_SET)].copy()
        pages = pages.loc[pages["created_at"].notna()].sort_values("created_at")
        if not pages.empty:
            first = pages.drop_duplicates("session_id", keep="first").copy()
            first["Módulo"] = first["evento"].map(MODULE_EVENT_TO_NAME)
            first_counts = first["Módulo"].value_counts().to_dict()

    rows = []
    for module in MODULE_PAGE_EVENTS:
        viewed = event_sessions(events, MODULE_PAGE_EVENTS[module])
        interested = event_sessions(events, MODULE_INTEREST_EVENTS[module])
        prioritized = event_sessions(events, MODULE_PRIORITY_EVENTS[module])
        rows.append(
            {
                "Módulo": module,
                "Sesiones que entraron": viewed,
                "% de visitas": round(viewed / visits * 100, 1) if visits else 0.0,
                "Primer módulo": int(first_counts.get(module, 0)),
                "Interés declarado": interested,
                "Votos prioridad": prioritized,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["Sesiones que entraron", "Votos prioridad", "Interés declarado"],
        ascending=False,
    ).reset_index(drop=True)


def build_source_table(events: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    columns = [
        label,
        "Visitas",
        "Primer clic",
        "Exploró módulo",
        "Diagnóstico",
        "Interés Beta",
        "Feedback",
        "% activación",
        "% módulo",
        "% Beta",
    ]
    if events.empty or group_col not in events.columns:
        return pd.DataFrame(columns=columns)

    rows = []
    for value, group in events.groupby(group_col, dropna=False):
        visits = event_sessions(group, "visita")
        first = event_sessions(group, "primera_interaccion")
        modules = module_explorers(group)
        diag = event_sessions(group, "diagnostico_visto")
        beta = event_sessions(group, "beta_interes")
        feedback = event_sessions(group, "feedback_enviado")
        rows.append(
            {
                label: str(value or "Sin dato"),
                "Visitas": visits,
                "Primer clic": first,
                "Exploró módulo": modules,
                "Diagnóstico": diag,
                "Interés Beta": beta,
                "Feedback": feedback,
                "% activación": round(first / visits * 100, 1) if visits else 0.0,
                "% módulo": round(modules / visits * 100, 1) if visits else 0.0,
                "% Beta": round(beta / visits * 100, 1) if visits else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values("Visitas", ascending=False).reset_index(drop=True)


def daily_activity(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or not {"created_at", "evento", "session_id"}.issubset(events.columns):
        return pd.DataFrame()
    ev = events.loc[events["created_at"].notna()].copy()
    if ev.empty:
        return pd.DataFrame()
    ev["Fecha"] = ev["created_at"].dt.tz_convert("America/Santiago").dt.date
    visits = (
        ev.loc[ev["evento"] == "visita"]
        .groupby("Fecha")["session_id"]
        .nunique()
        .rename("Visitas")
    )
    first = (
        ev.loc[ev["evento"] == "primera_interaccion"]
        .groupby("Fecha")["session_id"]
        .nunique()
        .rename("Primer clic")
    )
    modules = (
        ev.loc[ev["evento"].isin(MODULE_PAGE_EVENT_SET)]
        .groupby("Fecha")["session_id"]
        .nunique()
        .rename("Exploró módulo")
    )
    return pd.concat([visits, first, modules], axis=1).fillna(0).astype(int).sort_index()


def assert_cohort_consistency(events: pd.DataFrame) -> None:
    visits = event_sessions(events, "visita")
    modules = module_explorers(events)
    if modules > visits:
        raise AssertionError(f"Module explorers ({modules}) cannot exceed visits ({visits}) in the cohort")
