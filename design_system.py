from __future__ import annotations

import html

import streamlit as st


ACCENT = "#2457F5"
INK = "#162033"
MUTED = "#667085"
SURFACE = "#FFFFFF"
SOFT = "#F6F8FC"
BORDER = "#E7EAF0"
POSITIVE = "#12805C"
WARNING = "#B66A00"
DANGER = "#C9362B"


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --hc-accent:#2457F5;
            --hc-ink:#162033;
            --hc-muted:#667085;
            --hc-surface:#FFFFFF;
            --hc-soft:#F6F8FC;
            --hc-border:#E7EAF0;
            --hc-positive:#12805C;
            --hc-warning:#B66A00;
            --hc-danger:#C9362B;
        }
        html, body, [class*="css"] {font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
        .stApp {background:#F7F8FB; color:var(--hc-ink);}
        .block-container {max-width:1240px !important; padding-top:2rem !important; padding-bottom:4rem !important;}
        [data-testid="stSidebar"] {background:#111827 !important; border-right:0 !important;}
        [data-testid="stSidebar"] * {color:#E5E7EB;}
        [data-testid="stSidebar"] [role="radiogroup"] label {padding:.35rem .5rem; border-radius:10px;}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(255,255,255,.07);}
        [data-testid="stSidebar"] a {text-decoration:none;}
        [data-testid="stSidebar"] .stAlert {background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10);}
        h1,h2,h3 {letter-spacing:-.025em; color:var(--hc-ink);}
        h1 {font-weight:760 !important;}
        h2,h3 {font-weight:700 !important;}
        p, .stCaption {color:var(--hc-muted);}
        [data-testid="stMetric"] {
            background:#fff; border:1px solid var(--hc-border); border-radius:18px;
            padding:18px 18px 16px; box-shadow:0 1px 2px rgba(16,24,40,.03);
        }
        [data-testid="stMetricLabel"] {font-size:.82rem; color:#667085;}
        [data-testid="stMetricValue"] {font-weight:760; letter-spacing:-.035em; color:#101828;}
        [data-testid="stMetricDelta"] {font-size:.78rem;}
        .stButton>button, .stLinkButton>a {
            border-radius:12px !important; min-height:44px; font-weight:650 !important;
            box-shadow:none !important; transition:transform .12s ease, box-shadow .12s ease;
        }
        .stButton>button:hover, .stLinkButton>a:hover {transform:translateY(-1px);}
        .stButton>button[kind="primary"], .stLinkButton>a[kind="primary"] {background:#2457F5 !important; border-color:#2457F5 !important;}
        [data-testid="stDataFrame"] {border:1px solid var(--hc-border); border-radius:16px; overflow:hidden; background:#fff;}
        [data-baseweb="tab-list"] {gap:6px; background:#EEF1F6; border-radius:12px; padding:4px;}
        [data-baseweb="tab"] {border-radius:9px; padding:.55rem .9rem;}
        [data-baseweb="tab-highlight"] {display:none;}
        .hc-shell {background:#fff;border:1px solid var(--hc-border);border-radius:22px;padding:28px 30px;box-shadow:0 10px 35px rgba(16,24,40,.04);margin-bottom:18px;}
        .hc-eyebrow {font-size:.76rem;font-weight:750;text-transform:uppercase;letter-spacing:.12em;color:#2457F5;margin-bottom:8px;}
        .hc-hero-title {font-size:2.35rem;line-height:1.08;letter-spacing:-.045em;font-weight:790;color:#101828;max-width:820px;margin:0 0 12px;}
        .hc-hero-sub {font-size:1.05rem;line-height:1.65;color:#667085;max-width:760px;margin:0;}
        .hc-section-title {font-size:1.18rem;font-weight:730;color:#162033;margin:24px 0 4px;letter-spacing:-.02em;}
        .hc-section-sub {font-size:.9rem;color:#7A8494;margin-bottom:12px;}
        .hc-card {background:#fff;border:1px solid var(--hc-border);border-radius:18px;padding:20px;box-shadow:0 1px 2px rgba(16,24,40,.025);}
        .hc-card-label {font-size:.78rem;color:#7A8494;margin-bottom:7px;font-weight:650;}
        .hc-card-value {font-size:1.8rem;line-height:1.05;font-weight:780;letter-spacing:-.04em;color:#101828;}
        .hc-card-note {font-size:.8rem;color:#667085;margin-top:8px;line-height:1.4;}
        .hc-insight {background:#EEF4FF;border:1px solid #D7E3FF;border-radius:18px;padding:17px 19px;margin:12px 0 18px;color:#253B68;line-height:1.55;}
        .hc-insight b {color:#163B9C;}
        .hc-warning {background:#FFF7E8;border:1px solid #F4DBAE;border-radius:16px;padding:15px 17px;color:#6E4B13;margin:12px 0;}
        .hc-positive {background:#ECF8F2;border:1px solid #CBEBDD;border-radius:16px;padding:15px 17px;color:#275E4B;margin:12px 0;}
        .hc-pill {display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;background:#F2F4F7;color:#475467;font-size:.76rem;font-weight:650;}
        .hc-login-wrap {max-width:520px;margin:2.5rem auto 0;}
        .hc-login-card {background:#fff;border:1px solid var(--hc-border);border-radius:24px;padding:30px;box-shadow:0 18px 50px rgba(16,24,40,.07);}
        .hc-logo {display:inline-flex;width:42px;height:42px;border-radius:13px;align-items:center;justify-content:center;background:#2457F5;color:#fff;font-weight:800;margin-bottom:18px;}
        .hc-small {font-size:.8rem;color:#98A2B3;}
        .hc-divider {height:1px;background:#EEF0F4;margin:18px 0;}
        @media(max-width:768px){
          .block-container{padding:1.2rem .9rem 3rem !important;}
          .hc-shell{padding:22px 20px;border-radius:18px;}
          .hc-hero-title{font-size:1.85rem;}
          [data-testid="stMetric"]{padding:14px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(eyebrow: str, title: str, subtitle: str, badge: str | None = None) -> None:
    badge_html = f'<div style="margin-top:16px"><span class="hc-pill">{html.escape(badge)}</span></div>' if badge else ""
    st.markdown(
        f'<div class="hc-shell"><div class="hc-eyebrow">{html.escape(eyebrow)}</div>'
        f'<div class="hc-hero-title">{html.escape(title)}</div>'
        f'<div class="hc-hero-sub">{html.escape(subtitle)}</div>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="hc-section-title">{html.escape(title)}</div>'
        + (f'<div class="hc-section-sub">{html.escape(subtitle)}</div>' if subtitle else ""),
        unsafe_allow_html=True,
    )


def insight(title: str, body: str) -> None:
    st.markdown(f'<div class="hc-insight"><b>{html.escape(title)}</b><br>{html.escape(body)}</div>', unsafe_allow_html=True)
