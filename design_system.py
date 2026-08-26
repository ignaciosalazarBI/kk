from __future__ import annotations

import html

import streamlit as st


ACCENT = "#5B67F1"
INK = "#111827"
MUTED = "#667085"
SURFACE = "#FFFFFF"
SOFT = "#F5F7FB"
BORDER = "#E4E8F0"
POSITIVE = "#12A57A"
WARNING = "#D48616"
DANGER = "#D84A4A"


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cp-primary:#5B67F1;
            --cp-primary-2:#7C4DFF;
            --cp-cyan:#20C7D9;
            --cp-mint:#16C79A;
            --cp-ink:#111827;
            --cp-muted:#667085;
            --cp-border:#E4E8F0;
            --cp-bg:#F5F7FB;
            --cp-sidebar:#0B1020;
            --cp-sidebar-2:#11182A;
            --cp-positive:#12A57A;
            --cp-warning:#D48616;
            --cp-danger:#D84A4A;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-feature-settings:"tnum" 1, "cv11" 1;
        }
        body {background:var(--cp-bg);}
        .stApp {
            color:var(--cp-ink);
            background:
              radial-gradient(circle at 78% -8%, rgba(91,103,241,.11), transparent 28%),
              radial-gradient(circle at 38% 0%, rgba(32,199,217,.07), transparent 24%),
              linear-gradient(180deg,#F9FAFD 0%,#F4F6FB 100%);
        }
        .block-container {max-width:1320px !important;padding-top:1.35rem !important;padding-bottom:4.5rem !important;}
        [data-testid="stHeader"] {background:rgba(249,250,253,.78);backdrop-filter:blur(18px);border-bottom:1px solid rgba(228,232,240,.55);}
        [data-testid="stDecoration"] {display:none;}
        footer {visibility:hidden;}

        /* Sidebar */
        [data-testid="stSidebar"] {
            background:
              radial-gradient(circle at 20% 0%, rgba(91,103,241,.22), transparent 28%),
              linear-gradient(180deg,var(--cp-sidebar) 0%,#0A0F1D 100%) !important;
            border-right:1px solid rgba(255,255,255,.04) !important;
        }
        [data-testid="stSidebar"] > div:first-child {padding-top:1rem;}
        [data-testid="stSidebar"] * {color:#DCE3F4;}
        [data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.08);margin:.9rem 0;}
        [data-testid="stSidebar"] .stCaption {color:#8490A8 !important;}
        .hc-brand {display:flex;align-items:center;gap:11px;margin:4px 0 24px;padding:0 3px;}
        .hc-brand-mark {
            width:39px;height:39px;border-radius:13px;
            background:linear-gradient(135deg,#6B78FF 0%,#7257F5 52%,#20C7D9 120%);
            color:#fff;display:flex;align-items:center;justify-content:center;
            font-size:.78rem;font-weight:900;letter-spacing:-.035em;
            box-shadow:0 9px 24px rgba(91,103,241,.32),inset 0 1px 0 rgba(255,255,255,.28);
        }
        .hc-brand-name {font-size:1.02rem;font-weight:800;color:#fff;letter-spacing:-.025em;}
        .hc-brand-sub {font-size:.63rem;color:#8C98B3;letter-spacing:.12em;margin-top:2px;font-weight:700;}
        .hc-nav-label {font-size:.63rem;text-transform:uppercase;letter-spacing:.15em;font-weight:800;color:#727E98;margin:19px 10px 7px;}
        .hc-nav-link {
            display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:11px;
            text-decoration:none !important;color:#C9D2E7 !important;font-size:.87rem;font-weight:590;
            margin:3px 0;border:1px solid transparent;transition:all .16s ease;
        }
        .hc-nav-link:hover {background:rgba(255,255,255,.065);color:#fff !important;transform:translateX(2px);}
        .hc-nav-link.active {
            background:linear-gradient(90deg,rgba(91,103,241,.22),rgba(91,103,241,.08));
            color:#fff !important;border-color:rgba(129,140,248,.18);font-weight:720;
            box-shadow:inset 3px 0 0 #6F79F5;
        }
        .hc-nav-link.primary {
            position:relative;overflow:hidden;
            background:linear-gradient(135deg,#6875FF 0%,#5B67F1 48%,#7C4DFF 100%);
            color:#fff !important;font-weight:800;margin-bottom:15px;border-color:rgba(255,255,255,.13);
            box-shadow:0 11px 25px rgba(91,103,241,.25);
        }
        .hc-nav-link.primary:after {content:"→";margin-left:auto;font-size:1rem;opacity:.95;}
        .hc-nav-link.primary:hover {filter:brightness(1.08);transform:translateY(-1px);box-shadow:0 14px 30px rgba(91,103,241,.34);}
        .hc-nav-dot {width:8px;height:8px;border-radius:3px;background:#5B657C;display:inline-block;flex:none;transform:rotate(45deg);}
        .hc-nav-link.active .hc-nav-dot {background:#8E99FF;box-shadow:0 0 0 4px rgba(110,122,255,.12);}
        [data-testid="stSidebar"] [role="radiogroup"] label {padding:.48rem .58rem;border-radius:10px;transition:background .13s ease;}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(255,255,255,.06);}
        [data-testid="stSidebar"] a {text-decoration:none !important;}
        [data-testid="stSidebar"] .stAlert {background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.08);}

        /* Type */
        h1,h2,h3 {letter-spacing:-.035em;color:var(--cp-ink);}
        h1 {font-weight:830 !important;font-size:2.15rem !important;}
        h2 {font-weight:780 !important;font-size:1.42rem !important;}
        h3 {font-weight:740 !important;font-size:1.07rem !important;}
        p,.stCaption {color:var(--cp-muted);}

        /* Metrics */
        [data-testid="stMetric"] {
            position:relative;overflow:hidden;background:rgba(255,255,255,.94);
            border:1px solid rgba(224,229,238,.9);border-radius:17px;padding:19px 19px 17px;
            box-shadow:0 8px 26px rgba(23,30,50,.045),0 1px 2px rgba(23,30,50,.03);
            transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease;
        }
        [data-testid="stMetric"]:before {content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#6674FF,#8A5CFF,#21C6D8);opacity:.85;}
        [data-testid="stMetric"]:hover {transform:translateY(-2px);border-color:#CFD5F8;box-shadow:0 13px 34px rgba(62,73,150,.08);}
        [data-testid="stMetricLabel"] {font-size:.75rem;color:#707B8E;font-weight:680;letter-spacing:.015em;text-transform:uppercase;}
        [data-testid="stMetricValue"] {font-size:1.82rem;font-weight:830;letter-spacing:-.045em;color:#121827;line-height:1.14;margin-top:2px;}
        [data-testid="stMetricDelta"] {font-size:.74rem;margin-top:5px;font-weight:650;}

        /* Buttons */
        .stButton>button,.stFormSubmitButton>button,.stLinkButton>a {
            min-height:47px !important;border-radius:12px !important;padding:.62rem 1rem !important;
            font-size:.89rem !important;font-weight:760 !important;letter-spacing:-.01em !important;
            transition:all .16s ease !important;position:relative;overflow:hidden;
        }
        .stButton>button:active,.stFormSubmitButton>button:active,.stLinkButton>a:active {transform:translateY(1px) scale(.995);}
        .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stLinkButton>a[kind="primary"] {
            background:linear-gradient(135deg,#6674FF 0%,#5B67F1 46%,#7C4DFF 100%) !important;
            border:1px solid rgba(91,103,241,.2) !important;color:#fff !important;
            box-shadow:0 9px 20px rgba(91,103,241,.20),inset 0 1px 0 rgba(255,255,255,.25) !important;
        }
        .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover,.stLinkButton>a[kind="primary"]:hover {
            filter:brightness(1.06);transform:translateY(-2px);box-shadow:0 14px 28px rgba(91,103,241,.28) !important;
        }
        .stButton>button[kind="secondary"],.stLinkButton>a[kind="secondary"] {
            background:rgba(255,255,255,.95) !important;border:1px solid #DDE2EC !important;color:#20283A !important;
            box-shadow:0 3px 10px rgba(23,30,50,.035) !important;
        }
        .stButton>button[kind="secondary"]:hover,.stLinkButton>a[kind="secondary"]:hover {
            background:#fff !important;border-color:#BFC7F3 !important;color:#4A52C9 !important;transform:translateY(-1px);box-shadow:0 9px 20px rgba(66,77,145,.08) !important;
        }
        .stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stLinkButton>a:focus-visible {
            outline:3px solid rgba(91,103,241,.17) !important;outline-offset:2px !important;
        }

        /* Public choice buttons get a tile feel. */
        [data-testid="stButton"] button[kind="secondary"] {justify-content:flex-start;text-align:left;min-height:54px !important;}

        /* Inputs */
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="textarea"]>div {
            border-radius:12px !important;border-color:#DCE1EB !important;background:rgba(255,255,255,.98) !important;
            box-shadow:0 1px 2px rgba(16,24,40,.02) !important;transition:all .14s ease;
        }
        [data-baseweb="input"]>div:hover,[data-baseweb="select"]>div:hover,[data-baseweb="textarea"]>div:hover {border-color:#C7CEDE !important;}
        [data-baseweb="input"]>div:focus-within,[data-baseweb="select"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within {
            border-color:#8E97F3 !important;box-shadow:0 0 0 4px rgba(91,103,241,.09) !important;
        }
        [data-testid="stNumberInput"] button {border-radius:9px !important;}
        [data-testid="stExpander"] {background:rgba(255,255,255,.95);border:1px solid var(--cp-border);border-radius:15px !important;overflow:hidden;box-shadow:0 5px 16px rgba(23,30,50,.025);}
        [data-testid="stDataFrame"] {border:1px solid var(--cp-border);border-radius:15px;overflow:hidden;background:#fff;box-shadow:0 7px 24px rgba(23,30,50,.035);}

        /* Tabs */
        [data-baseweb="tab-list"] {gap:3px;background:#EDEFFC;border-radius:12px;padding:4px;width:max-content;max-width:100%;border:1px solid #E1E4F6;}
        [data-baseweb="tab"] {border-radius:9px;padding:.52rem .88rem;font-size:.84rem;font-weight:700;color:#65708A;}
        [data-baseweb="tab"][aria-selected="true"] {background:#fff !important;color:#414AB4 !important;box-shadow:0 3px 10px rgba(79,88,169,.10);}
        [data-baseweb="tab-highlight"] {display:none;}

        /* Public hero */
        .hero {
            background:
              radial-gradient(circle at 92% 10%, rgba(32,199,217,.30), transparent 21%),
              radial-gradient(circle at 70% 80%, rgba(124,77,255,.25), transparent 32%),
              linear-gradient(135deg,#10162A 0%,#18224A 48%,#2B2460 100%) !important;
            border:1px solid rgba(113,126,255,.24) !important;border-radius:25px !important;padding:43px 43px !important;
            box-shadow:0 25px 65px rgba(31,37,84,.18) !important;position:relative;overflow:hidden;
        }
        .hero:before {content:"";position:absolute;left:auto;right:-70px;top:-95px;width:240px;height:240px;border-radius:50%;background:linear-gradient(135deg,rgba(98,110,255,.36),rgba(32,199,217,.12));filter:blur(2px);}
        .hero:after {content:"CONTROL • DECISIÓN • CRECIMIENTO";position:absolute;right:28px;bottom:20px;color:rgba(255,255,255,.22);font-size:.62rem;letter-spacing:.16em;font-weight:800;}
        .hero h1 {font-size:2.65rem !important;line-height:1.04 !important;letter-spacing:-.055em !important;color:#fff !important;max-width:830px;margin-bottom:14px !important;text-shadow:0 3px 18px rgba(0,0,0,.12);}
        .hero p {font-size:1.05rem !important;line-height:1.65 !important;color:#C9D2EA !important;max-width:720px;}
        .answer-card,.finance-callout,.insight {
            background:linear-gradient(135deg,#F1F4FF,#F6FBFF) !important;border:1px solid #D9DFFB !important;border-radius:16px !important;
            color:#344064 !important;box-shadow:0 8px 25px rgba(72,82,151,.055) !important;
        }
        .demo-banner,.beta-note {background:#FFF9EA !important;border:1px solid #F1E0B3 !important;border-radius:13px !important;color:#6D5823 !important;}
        .module-card {
            background:rgba(255,255,255,.96) !important;border:1px solid var(--cp-border) !important;border-radius:17px !important;
            padding:20px !important;min-height:112px !important;box-shadow:0 9px 26px rgba(23,30,50,.035) !important;transition:all .16s ease;
        }
        .module-card:hover {transform:translateY(-3px);border-color:#CDD3F7 !important;box-shadow:0 15px 34px rgba(73,84,160,.08) !important;}
        .kpi {background:rgba(255,255,255,.97) !important;border:1px solid var(--cp-border) !important;border-radius:17px !important;padding:19px !important;box-shadow:0 9px 25px rgba(23,30,50,.04) !important;}
        .kpi .label {color:#758097 !important;font-weight:680;letter-spacing:.01em;}
        .kpi .value {color:#101827 !important;letter-spacing:-.045em;font-size:1.78rem !important;}

        /* Finance / product hero */
        .hc-shell {
            position:relative;overflow:hidden;
            background:
              radial-gradient(circle at 90% 0%,rgba(32,199,217,.18),transparent 24%),
              radial-gradient(circle at 62% 110%,rgba(124,77,255,.22),transparent 32%),
              linear-gradient(135deg,#10162A 0%,#171F3D 60%,#231C50 100%);
            border:1px solid rgba(112,124,255,.20);border-radius:24px;padding:32px 33px;
            box-shadow:0 22px 55px rgba(35,42,93,.16);margin-bottom:20px;
        }
        .hc-shell:after {content:"";position:absolute;right:-48px;top:-58px;width:180px;height:180px;border-radius:50%;border:28px solid rgba(255,255,255,.035);}
        .hc-eyebrow {font-size:.69rem;font-weight:820;text-transform:uppercase;letter-spacing:.15em;color:#8EA1FF;margin-bottom:9px;}
        .hc-hero-title {font-size:2.35rem;line-height:1.04;letter-spacing:-.052em;font-weight:850;color:#fff;max-width:840px;margin:0 0 13px;}
        .hc-hero-sub {font-size:1.01rem;line-height:1.65;color:#BCC7DF;max-width:760px;margin:0;}
        .hc-section-title {font-size:1.09rem;font-weight:790;color:#1B2234;margin:27px 0 4px;letter-spacing:-.025em;}
        .hc-section-sub {font-size:.84rem;color:#7D879B;margin-bottom:12px;}
        .hc-card {background:#fff;border:1px solid var(--cp-border);border-radius:16px;padding:20px;box-shadow:0 8px 24px rgba(23,30,50,.035);}
        .hc-card-label {font-size:.73rem;color:#7D879B;margin-bottom:7px;font-weight:680;text-transform:uppercase;letter-spacing:.04em;}
        .hc-card-value {font-size:1.76rem;line-height:1.05;font-weight:840;letter-spacing:-.045em;color:#101827;}
        .hc-card-note {font-size:.78rem;color:#687386;margin-top:8px;line-height:1.42;}
        .hc-insight {background:linear-gradient(135deg,#EEF2FF,#F2FBFF);border:1px solid #D8DEFB;border-radius:16px;padding:17px 19px;margin:12px 0 18px;color:#354369;line-height:1.55;box-shadow:0 8px 22px rgba(72,82,151,.04);}
        .hc-insight b {color:#4650C5;}
        .hc-warning {background:#FFF8E9;border:1px solid #F0DDB5;border-radius:14px;padding:15px 17px;color:#72511D;margin:12px 0;}
        .hc-positive {background:#EDFBF7;border:1px solid #C6EEE1;border-radius:14px;padding:15px 17px;color:#215D4A;margin:12px 0;}
        .hc-pill {display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.10);color:#D7DDF5;font-size:.72rem;font-weight:720;}
        .hc-login-wrap {max-width:540px;margin:2.2rem auto 0;}
        .hc-login-card {background:#fff;border:1px solid var(--cp-border);border-radius:20px;padding:30px;box-shadow:0 20px 46px rgba(27,34,70,.09);}
        .hc-logo {display:inline-flex;width:42px;height:42px;border-radius:13px;align-items:center;justify-content:center;background:linear-gradient(135deg,#6875FF,#7C4DFF);color:#fff;font-weight:900;margin-bottom:18px;box-shadow:0 8px 20px rgba(91,103,241,.20);}
        .hc-small {font-size:.78rem;color:#96A0B2;}
        .hc-divider {height:1px;background:#E8EBF2;margin:18px 0;}

        /* Simple visual rhythm helpers */
        .cp-topbar {display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px;}
        .cp-title {font-size:2rem;font-weight:850;letter-spacing:-.045em;color:#111827;line-height:1.05;}
        .cp-subtitle {font-size:.9rem;color:#768196;margin-top:5px;}
        .cp-live {display:inline-flex;align-items:center;gap:7px;padding:7px 11px;border-radius:999px;background:#EAFBF6;color:#14765B;font-size:.72rem;font-weight:760;border:1px solid #CEEFE4;}
        .cp-live:before {content:"";width:7px;height:7px;border-radius:50%;background:#16B587;box-shadow:0 0 0 4px rgba(22,181,135,.10);}

        @media(max-width:768px){
          .block-container{padding:1rem .78rem 3rem !important;}
          .hero{padding:30px 24px !important;border-radius:20px !important;}
          .hero h1{font-size:2rem !important;}
          .hero:after{display:none;}
          .hc-shell{padding:25px 22px;border-radius:19px;}
          .hc-hero-title{font-size:1.9rem !important;}
          [data-testid="stMetric"]{padding:15px;border-radius:14px;}
          [data-testid="stMetricValue"]{font-size:1.5rem;}
          [data-baseweb="tab-list"]{width:100%;overflow-x:auto;}
          .cp-topbar{align-items:flex-start;flex-direction:column;}
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
    st.markdown(
        f'<div class="hc-insight"><b>{html.escape(title)}</b><br>{html.escape(body)}</div>',
        unsafe_allow_html=True,
    )
