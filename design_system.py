from __future__ import annotations

import html

import streamlit as st


ACCENT = "#2367E8"
INK = "#132333"
MUTED = "#687786"
SURFACE = "#FFFFFF"
SOFT = "#F4F7F9"
BORDER = "#DDE5EB"
POSITIVE = "#16805B"
WARNING = "#A96316"
DANGER = "#C43B3B"


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --hc-accent:#2367E8;
            --hc-accent-dark:#1755C6;
            --hc-ink:#132333;
            --hc-muted:#687786;
            --hc-surface:#FFFFFF;
            --hc-soft:#F4F7F9;
            --hc-border:#DDE5EB;
            --hc-positive:#16805B;
            --hc-warning:#A96316;
            --hc-danger:#C43B3B;
            --hc-sidebar:#102735;
            --hc-sidebar-soft:#183746;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-feature-settings:"tnum" 1, "cv11" 1;
        }
        .stApp {background:#F4F7F9;color:var(--hc-ink);}
        .block-container {max-width:1280px !important;padding-top:1.55rem !important;padding-bottom:4rem !important;}
        [data-testid="stHeader"] {background:rgba(244,247,249,.92);backdrop-filter:blur(10px);}
        [data-testid="stDecoration"] {display:none;}
        footer {visibility:hidden;}

        /* Sidebar: quiet, product-like navigation. */
        [data-testid="stSidebar"] {background:var(--hc-sidebar) !important;border-right:0 !important;}
        [data-testid="stSidebar"] > div:first-child {padding-top:1rem;}
        [data-testid="stSidebar"] * {color:#DCE6EB;}
        [data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.09);margin:.85rem 0;}
        [data-testid="stSidebar"] .stCaption {color:#8FA4AF !important;}
        .hc-brand {display:flex;align-items:center;gap:10px;margin:2px 0 22px;}
        .hc-brand-mark {width:34px;height:34px;border-radius:9px;background:#31C7A7;color:#0A2A2B;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:850;letter-spacing:-.03em;}
        .hc-brand-name {font-size:1rem;font-weight:760;color:#fff;letter-spacing:-.02em;}
        .hc-brand-sub {font-size:.66rem;color:#8FA4AF;letter-spacing:.04em;margin-top:1px;}
        .hc-nav-label {font-size:.66rem;text-transform:uppercase;letter-spacing:.13em;font-weight:750;color:#8299A5;margin:17px 8px 6px;}
        .hc-nav-link {display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:9px;text-decoration:none !important;color:#DCE6EB !important;font-size:.88rem;font-weight:570;margin:2px 0;border:1px solid transparent;transition:background .12s ease,border-color .12s ease,color .12s ease;}
        .hc-nav-link:hover {background:rgba(255,255,255,.065);color:#fff !important;}
        .hc-nav-link.active {background:#1B4050;color:#fff !important;border-color:rgba(255,255,255,.07);font-weight:690;}
        .hc-nav-link.primary {background:#31C7A7;color:#092C2D !important;font-weight:760;margin-bottom:14px;}
        .hc-nav-link.primary:hover {background:#48D0B3;color:#092C2D !important;}
        .hc-nav-dot {width:7px;height:7px;border-radius:50%;background:#78909B;display:inline-block;flex:none;}
        .hc-nav-link.active .hc-nav-dot {background:#31C7A7;box-shadow:0 0 0 3px rgba(49,199,167,.12);}
        [data-testid="stSidebar"] [role="radiogroup"] label {padding:.46rem .55rem;border-radius:9px;transition:background .12s ease;}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(255,255,255,.065);}
        [data-testid="stSidebar"] a {text-decoration:none !important;}
        [data-testid="stSidebar"] .stAlert {background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.09);}

        /* Typography hierarchy. */
        h1,h2,h3 {letter-spacing:-.03em;color:var(--hc-ink);}
        h1 {font-weight:780 !important;font-size:2rem !important;}
        h2 {font-weight:730 !important;font-size:1.35rem !important;}
        h3 {font-weight:700 !important;font-size:1.05rem !important;}
        p,.stCaption {color:var(--hc-muted);}

        /* Metrics: numbers first, decoration last. */
        [data-testid="stMetric"] {background:#fff;border:1px solid var(--hc-border);border-radius:13px;padding:17px 17px 15px;box-shadow:0 1px 2px rgba(13,34,51,.025);}
        [data-testid="stMetricLabel"] {font-size:.76rem;color:#71808D;font-weight:580;letter-spacing:.005em;}
        [data-testid="stMetricValue"] {font-size:1.68rem;font-weight:770;letter-spacing:-.04em;color:#102332;line-height:1.2;}
        [data-testid="stMetricDelta"] {font-size:.74rem;margin-top:3px;}

        /* Buttons: one consistent component language. */
        .stButton>button,.stFormSubmitButton>button,.stLinkButton>a {
            min-height:44px !important;border-radius:9px !important;padding:.56rem .92rem !important;
            font-size:.88rem !important;font-weight:680 !important;letter-spacing:-.005em !important;
            box-shadow:0 1px 1px rgba(16,39,53,.03) !important;transition:background .12s ease,border-color .12s ease,box-shadow .12s ease,transform .08s ease !important;
        }
        .stButton>button:active,.stFormSubmitButton>button:active,.stLinkButton>a:active {transform:translateY(1px);}
        .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stLinkButton>a[kind="primary"] {
            background:var(--hc-accent) !important;border:1px solid var(--hc-accent) !important;color:#fff !important;
        }
        .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover,.stLinkButton>a[kind="primary"]:hover {
            background:var(--hc-accent-dark) !important;border-color:var(--hc-accent-dark) !important;box-shadow:0 5px 14px rgba(35,103,232,.15) !important;
        }
        .stButton>button[kind="secondary"],.stLinkButton>a[kind="secondary"] {
            background:#fff !important;border:1px solid #D6E0E7 !important;color:#203442 !important;
        }
        .stButton>button[kind="secondary"]:hover,.stLinkButton>a[kind="secondary"]:hover {
            background:#F8FAFB !important;border-color:#BFCED8 !important;color:#102735 !important;
        }
        .stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stLinkButton>a:focus-visible {
            outline:3px solid rgba(35,103,232,.16) !important;outline-offset:2px !important;
        }

        /* Inputs and controls should feel like a single product. */
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="textarea"]>div {
            border-radius:9px !important;border-color:#D6E0E7 !important;background:#fff !important;box-shadow:none !important;
        }
        [data-baseweb="input"]>div:focus-within,[data-baseweb="select"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within {
            border-color:#7EA8F4 !important;box-shadow:0 0 0 3px rgba(35,103,232,.09) !important;
        }
        [data-testid="stNumberInput"] button {border-radius:7px !important;}
        [data-testid="stExpander"] {background:#fff;border:1px solid var(--hc-border);border-radius:12px !important;overflow:hidden;}
        [data-testid="stDataFrame"] {border:1px solid var(--hc-border);border-radius:12px;overflow:hidden;background:#fff;}

        /* Tabs: calm segmented control instead of decorative pills. */
        [data-baseweb="tab-list"] {gap:2px;background:#EAF0F4;border-radius:10px;padding:3px;width:max-content;max-width:100%;}
        [data-baseweb="tab"] {border-radius:8px;padding:.48rem .82rem;font-size:.84rem;font-weight:620;color:#61717E;}
        [data-baseweb="tab"][aria-selected="true"] {background:#fff !important;color:#142A39 !important;box-shadow:0 1px 3px rgba(16,39,53,.07);}
        [data-baseweb="tab-highlight"] {display:none;}

        /* Existing public Beta, reskinned without touching its behavior. */
        .hero {background:#fff !important;border:1px solid var(--hc-border) !important;border-radius:15px !important;padding:34px 36px !important;box-shadow:0 4px 18px rgba(16,39,53,.035) !important;position:relative;overflow:hidden;}
        .hero:before {content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#31C7A7;}
        .hero h1 {font-size:2.15rem !important;line-height:1.1 !important;letter-spacing:-.045em !important;color:#102332 !important;max-width:850px;margin-bottom:12px !important;}
        .hero p {font-size:1rem !important;line-height:1.6 !important;color:#687786 !important;max-width:760px;}
        .answer-card,.finance-callout,.insight {background:#F1F6FF !important;border:1px solid #D7E5FB !important;border-radius:12px !important;color:#304B69 !important;box-shadow:none !important;}
        .demo-banner,.beta-note {background:#FFFBF2 !important;border:1px solid #EFE1BC !important;border-radius:10px !important;color:#705B2C !important;}
        .module-card {background:#fff !important;border:1px solid var(--hc-border) !important;border-radius:12px !important;padding:18px !important;min-height:108px !important;box-shadow:none !important;}
        .kpi {background:#fff !important;border:1px solid var(--hc-border) !important;border-radius:12px !important;padding:18px !important;box-shadow:none !important;}
        .kpi .label {color:#758491 !important;font-weight:600;}
        .kpi .value {color:#102332 !important;letter-spacing:-.04em;}

        /* Product components. */
        .hc-shell {background:#fff;border:1px solid var(--hc-border);border-radius:15px;padding:27px 29px;box-shadow:0 4px 18px rgba(16,39,53,.035);margin-bottom:17px;}
        .hc-eyebrow {font-size:.7rem;font-weight:760;text-transform:uppercase;letter-spacing:.12em;color:#4A718A;margin-bottom:8px;}
        .hc-hero-title {font-size:2.1rem;line-height:1.08;letter-spacing:-.045em;font-weight:790;color:#102332;max-width:820px;margin:0 0 11px;}
        .hc-hero-sub {font-size:1rem;line-height:1.62;color:#687786;max-width:760px;margin:0;}
        .hc-section-title {font-size:1.05rem;font-weight:720;color:#183041;margin:24px 0 3px;letter-spacing:-.02em;}
        .hc-section-sub {font-size:.83rem;color:#7B8A96;margin-bottom:11px;}
        .hc-card {background:#fff;border:1px solid var(--hc-border);border-radius:12px;padding:19px;box-shadow:none;}
        .hc-card-label {font-size:.74rem;color:#7B8A96;margin-bottom:7px;font-weight:620;}
        .hc-card-value {font-size:1.7rem;line-height:1.05;font-weight:780;letter-spacing:-.04em;color:#102332;}
        .hc-card-note {font-size:.77rem;color:#687786;margin-top:8px;line-height:1.4;}
        .hc-insight {background:#EEF5FF;border:1px solid #D6E5FA;border-radius:12px;padding:16px 18px;margin:11px 0 17px;color:#34516D;line-height:1.52;}
        .hc-insight b {color:#1D4F7B;}
        .hc-warning {background:#FFF7EA;border:1px solid #EFDEBE;border-radius:11px;padding:14px 16px;color:#6E501E;margin:11px 0;}
        .hc-positive {background:#EDF8F3;border:1px solid #CDE9DC;border-radius:11px;padding:14px 16px;color:#285D4C;margin:11px 0;}
        .hc-pill {display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;background:#EFF3F6;color:#526572;font-size:.72rem;font-weight:650;}
        .hc-login-wrap {max-width:520px;margin:2.2rem auto 0;}
        .hc-login-card {background:#fff;border:1px solid var(--hc-border);border-radius:16px;padding:29px;box-shadow:0 12px 36px rgba(16,39,53,.06);}
        .hc-logo {display:inline-flex;width:40px;height:40px;border-radius:10px;align-items:center;justify-content:center;background:#31C7A7;color:#0A2A2B;font-weight:850;margin-bottom:18px;}
        .hc-small {font-size:.78rem;color:#91A0AA;}
        .hc-divider {height:1px;background:#E9EEF2;margin:18px 0;}

        @media(max-width:768px){
          .block-container{padding:1rem .82rem 3rem !important;}
          .hero{padding:23px 20px !important;border-radius:13px !important;}
          .hero h1,.hc-hero-title{font-size:1.72rem !important;}
          .hc-shell{padding:21px 19px;border-radius:13px;}
          [data-testid="stMetric"]{padding:14px;border-radius:11px;}
          [data-testid="stMetricValue"]{font-size:1.45rem;}
          [data-baseweb="tab-list"]{width:100%;overflow-x:auto;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(eyebrow: str, title: str, subtitle: str, badge: str | None = None) -> None:
    badge_html = f'<div style="margin-top:15px"><span class="hc-pill">{html.escape(badge)}</span></div>' if badge else ""
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
