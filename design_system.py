from __future__ import annotations

import html

import streamlit as st


ACCENT = "#2F6BFF"
INK = "#101828"
MUTED = "#667085"
SURFACE = "#FFFFFF"
SOFT = "#F6F8FC"
BORDER = "#E5E9F0"
POSITIVE = "#168A63"
WARNING = "#B66A14"
DANGER = "#C9413A"


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cp-accent:#2F6BFF;
            --cp-accent-hover:#2458D8;
            --cp-ink:#101828;
            --cp-muted:#667085;
            --cp-subtle:#98A2B3;
            --cp-surface:#FFFFFF;
            --cp-soft:#F6F8FC;
            --cp-border:#E5E9F0;
            --cp-positive:#168A63;
            --cp-warning:#B66A14;
            --cp-danger:#C9413A;
            --cp-sidebar:#101828;
            --cp-sidebar-active:#1D2939;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-feature-settings:"tnum" 1, "cv11" 1;
        }
        .stApp {background:var(--cp-soft);color:var(--cp-ink);}
        .block-container {max-width:1280px !important;padding-top:1.45rem !important;padding-bottom:4rem !important;}
        footer,[data-testid="stDecoration"]{display:none !important;}
        [data-testid="stHeader"]{background:rgba(246,248,252,.92);backdrop-filter:blur(10px);}
        [data-testid="stToolbarActions"]{display:none !important;}

        /* Remove Streamlit's automatic multipage nav and the legacy radio navigation.
           We keep one deliberate product navigation only. */
        [data-testid="stSidebarNav"]{display:none !important;}
        [data-testid="stSidebar"] [role="radiogroup"]{display:none !important;}
        [data-testid="stSidebar"] [data-testid="stAlert"]{display:none !important;}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"]{display:none !important;}

        /* Product sidebar */
        [data-testid="stSidebar"]{
            background:var(--cp-sidebar) !important;
            border-right:1px solid rgba(255,255,255,.05) !important;
            width:276px !important;
            min-width:276px !important;
        }
        [data-testid="stSidebar"] > div:first-child{padding:1.15rem .85rem 1.1rem !important;overflow-y:auto;}
        [data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.07);margin:.85rem .2rem;}
        [data-testid="stSidebar"] a{text-decoration:none !important;}

        .cp-brand{display:flex;align-items:center;gap:11px;padding:2px 7px 19px;}
        .cp-brand-mark{width:36px;height:36px;border-radius:10px;background:#2F6BFF;display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:.78rem;box-shadow:0 6px 18px rgba(47,107,255,.25);}
        .cp-brand-title{font-size:.98rem;line-height:1.1;font-weight:750;letter-spacing:-.02em;color:#fff;}
        .cp-brand-sub{font-size:.67rem;line-height:1.2;color:#7F8DA3;margin-top:4px;letter-spacing:.06em;text-transform:uppercase;font-weight:650;}
        .cp-nav-section{font-size:.64rem;text-transform:uppercase;letter-spacing:.12em;font-weight:720;color:#66758A;margin:18px 9px 7px;}
        .cp-nav-link{display:flex;align-items:center;gap:10px;min-height:42px;padding:9px 10px;margin:2px 0;border-radius:9px;color:#C8D1DE !important;font-size:.88rem;font-weight:560;line-height:1.2;border:1px solid transparent;transition:background .12s ease,color .12s ease,border-color .12s ease;}
        .cp-nav-link svg{width:17px;height:17px;stroke:#7F8DA3;flex:none;transition:stroke .12s ease;}
        .cp-nav-link:hover{background:rgba(255,255,255,.055);color:#fff !important;}
        .cp-nav-link:hover svg{stroke:#B9C5D5;}
        .cp-nav-link.active{background:var(--cp-sidebar-active);color:#fff !important;border-color:rgba(255,255,255,.055);font-weight:680;}
        .cp-nav-link.active svg{stroke:#6F9BFF;}
        .cp-nav-link.cta{background:#fff;color:#101828 !important;font-weight:720;margin:2px 0 14px;box-shadow:0 5px 16px rgba(0,0,0,.14);}
        .cp-nav-link.cta svg{stroke:#2F6BFF;}
        .cp-nav-link.cta:hover{background:#F7F9FC;color:#101828 !important;}
        .cp-sidebar-note{font-size:.72rem;line-height:1.45;color:#66758A;padding:12px 10px 3px;}
        .cp-soon{padding:8px 10px;color:#66758A;font-size:.82rem;display:flex;align-items:center;gap:9px;}
        .cp-soon:before{content:"";width:6px;height:6px;border-radius:50%;background:#344054;flex:none;}

        /* Typography */
        h1,h2,h3{color:var(--cp-ink);letter-spacing:-.03em;}
        h1{font-size:2rem !important;font-weight:760 !important;line-height:1.15 !important;}
        h2{font-size:1.3rem !important;font-weight:720 !important;}
        h3{font-size:1.02rem !important;font-weight:680 !important;}
        p,.stCaption{color:var(--cp-muted);}

        /* Buttons: solid action, neutral secondary, quiet navigation. */
        .stButton>button,.stFormSubmitButton>button,.stLinkButton>a{
            min-height:46px !important;border-radius:10px !important;padding:.58rem 1rem !important;
            font-size:.88rem !important;font-weight:680 !important;letter-spacing:-.006em !important;
            box-shadow:none !important;transition:background .12s ease,border-color .12s ease,box-shadow .12s ease,transform .08s ease !important;
        }
        .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stLinkButton>a[kind="primary"]{
            background:var(--cp-accent) !important;border:1px solid var(--cp-accent) !important;color:#fff !important;
        }
        .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover,.stLinkButton>a[kind="primary"]:hover{
            background:var(--cp-accent-hover) !important;border-color:var(--cp-accent-hover) !important;box-shadow:0 5px 14px rgba(47,107,255,.18) !important;
        }
        .stButton>button[kind="secondary"],.stLinkButton>a[kind="secondary"]{
            background:#fff !important;border:1px solid #D7DEE8 !important;color:#253247 !important;
        }
        .stButton>button[kind="secondary"]:hover,.stLinkButton>a[kind="secondary"]:hover{
            background:#F9FAFC !important;border-color:#BFC9D8 !important;color:#101828 !important;
        }
        .stButton>button:active,.stFormSubmitButton>button:active,.stLinkButton>a:active{transform:translateY(1px);}
        .stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stLinkButton>a:focus-visible{outline:3px solid rgba(47,107,255,.16) !important;outline-offset:2px !important;}

        /* Homepage decision buttons: card-like, same hierarchy for every pain point. */
        .st-key-first_0 button,.st-key-first_1 button,.st-key-first_2 button,.st-key-first_3 button,
        .st-key-first_4 button,.st-key-first_5 button,.st-key-first_6 button,.st-key-first_7 button{
            background:#fff !important;color:#1D2939 !important;border:1px solid #E0E5ED !important;
            min-height:58px !important;justify-content:flex-start !important;text-align:left !important;
            padding:.75rem 1rem !important;font-weight:650 !important;box-shadow:0 1px 2px rgba(16,24,40,.025) !important;
        }
        .st-key-first_0 button:hover,.st-key-first_1 button:hover,.st-key-first_2 button:hover,.st-key-first_3 button:hover,
        .st-key-first_4 button:hover,.st-key-first_5 button:hover,.st-key-first_6 button:hover,.st-key-first_7 button:hover{
            background:#F8FAFF !important;border-color:#9BB8FF !important;color:#1749B8 !important;box-shadow:0 4px 14px rgba(47,107,255,.08) !important;transform:translateY(-1px);
        }

        /* Inputs */
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="textarea"]>div{
            background:#fff !important;border:1px solid #D9E0E9 !important;border-radius:10px !important;box-shadow:none !important;
        }
        [data-baseweb="input"]>div:focus-within,[data-baseweb="select"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within{
            border-color:#86A6FF !important;box-shadow:0 0 0 3px rgba(47,107,255,.10) !important;
        }
        [data-testid="stExpander"]{background:#fff;border:1px solid var(--cp-border);border-radius:12px !important;overflow:hidden;}
        [data-testid="stDataFrame"]{background:#fff;border:1px solid var(--cp-border);border-radius:12px;overflow:hidden;}

        /* Metrics and data surfaces */
        [data-testid="stMetric"]{background:#fff;border:1px solid var(--cp-border);border-radius:12px;padding:17px 17px 15px;box-shadow:0 1px 2px rgba(16,24,40,.025);}
        [data-testid="stMetricLabel"]{font-size:.76rem;color:#667085;font-weight:590;}
        [data-testid="stMetricValue"]{font-size:1.65rem;color:#101828;font-weight:760;letter-spacing:-.04em;line-height:1.18;}
        [data-testid="stMetricDelta"]{font-size:.74rem;margin-top:3px;}
        [data-baseweb="tab-list"]{gap:2px;background:#EEF1F6;border-radius:10px;padding:3px;width:max-content;max-width:100%;}
        [data-baseweb="tab"]{border-radius:8px;padding:.48rem .82rem;font-size:.84rem;font-weight:610;color:#667085;}
        [data-baseweb="tab"][aria-selected="true"]{background:#fff !important;color:#101828 !important;box-shadow:0 1px 3px rgba(16,24,40,.08);}
        [data-baseweb="tab-highlight"]{display:none;}

        /* Public hero and reusable cards */
        .hero{background:linear-gradient(145deg,#FFFFFF 0%,#F8FAFF 100%) !important;border:1px solid #E2E7EF !important;border-radius:16px !important;padding:36px 38px !important;box-shadow:0 8px 30px rgba(16,24,40,.045) !important;position:relative;overflow:hidden;margin-bottom:18px !important;}
        .hero:after{content:"";position:absolute;width:240px;height:240px;border-radius:50%;right:-130px;top:-145px;background:radial-gradient(circle,rgba(47,107,255,.11),rgba(47,107,255,0) 68%);pointer-events:none;}
        .hero h1{font-size:2.25rem !important;line-height:1.08 !important;letter-spacing:-.045em !important;color:#101828 !important;max-width:830px;margin:0 0 12px !important;}
        .hero p{font-size:1rem !important;line-height:1.65 !important;color:#667085 !important;max-width:730px;margin:0 !important;}
        .answer-card,.finance-callout,.insight{background:#F5F8FF !important;border:1px solid #DCE6FF !important;border-radius:12px !important;color:#31456B !important;box-shadow:none !important;}
        .demo-banner,.beta-note{background:#FFFBF3 !important;border:1px solid #EFE1C2 !important;border-radius:10px !important;color:#6F5724 !important;}
        .module-card,.kpi{background:#fff !important;border:1px solid var(--cp-border) !important;border-radius:12px !important;box-shadow:0 1px 2px rgba(16,24,40,.02) !important;}
        .module-card{padding:18px !important;min-height:108px !important;}
        .kpi{padding:18px !important;}
        .kpi .label{color:#667085 !important;font-weight:600;}
        .kpi .value{color:#101828 !important;letter-spacing:-.04em;}

        /* Authenticated finance product surfaces */
        .hc-shell{background:#fff;border:1px solid var(--cp-border);border-radius:15px;padding:28px 30px;box-shadow:0 5px 22px rgba(16,24,40,.04);margin-bottom:18px;}
        .hc-eyebrow{font-size:.69rem;font-weight:750;text-transform:uppercase;letter-spacing:.12em;color:#2F6BFF;margin-bottom:8px;}
        .hc-hero-title{font-size:2.08rem;line-height:1.08;letter-spacing:-.045em;font-weight:775;color:#101828;max-width:820px;margin:0 0 11px;}
        .hc-hero-sub{font-size:1rem;line-height:1.62;color:#667085;max-width:760px;margin:0;}
        .hc-section-title{font-size:1.05rem;font-weight:700;color:#1D2939;margin:24px 0 3px;letter-spacing:-.02em;}
        .hc-section-sub{font-size:.83rem;color:#7B8493;margin-bottom:11px;}
        .hc-card{background:#fff;border:1px solid var(--cp-border);border-radius:12px;padding:19px;box-shadow:none;}
        .hc-card-label{font-size:.74rem;color:#7B8493;margin-bottom:7px;font-weight:620;}
        .hc-card-value{font-size:1.7rem;line-height:1.05;font-weight:760;letter-spacing:-.04em;color:#101828;}
        .hc-card-note{font-size:.77rem;color:#667085;margin-top:8px;line-height:1.4;}
        .hc-insight{background:#F3F7FF;border:1px solid #DBE5FF;border-radius:12px;padding:16px 18px;margin:11px 0 17px;color:#345071;line-height:1.52;}
        .hc-insight b{color:#1749B8;}
        .hc-warning{background:#FFF8ED;border:1px solid #F0DEC0;border-radius:11px;padding:14px 16px;color:#6D4D1C;margin:11px 0;}
        .hc-positive{background:#EEF8F4;border:1px solid #CDE8DD;border-radius:11px;padding:14px 16px;color:#285D4D;margin:11px 0;}
        .hc-pill{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;background:#EFF3F8;color:#526071;font-size:.72rem;font-weight:650;}
        .hc-login-wrap{max-width:520px;margin:2.2rem auto 0;}
        .hc-login-card{background:#fff;border:1px solid var(--cp-border);border-radius:15px;padding:29px;box-shadow:0 10px 34px rgba(16,24,40,.06);}
        .hc-logo{display:inline-flex;width:40px;height:40px;border-radius:10px;align-items:center;justify-content:center;background:#2F6BFF;color:#fff;font-weight:800;margin-bottom:18px;}
        .hc-small{font-size:.78rem;color:#98A2B3;}
        .hc-divider{height:1px;background:#EAECF0;margin:18px 0;}

        @media(max-width:768px){
            [data-testid="stSidebar"]{width:min(86vw,320px) !important;min-width:min(86vw,320px) !important;max-width:320px !important;}
            [data-testid="stSidebar"] > div:first-child{padding:1rem .72rem 1.2rem !important;}
            .cp-brand{padding-bottom:13px;}
            .cp-nav-section{margin-top:13px;}
            .cp-nav-link{min-height:43px;font-size:.9rem;padding:9px 10px;}
            .cp-nav-secondary{display:none !important;}
            .cp-sidebar-note{display:none !important;}
            .block-container{padding:1rem .82rem 3rem !important;}
            .hero{padding:24px 21px !important;border-radius:13px !important;}
            .hero h1,.hc-hero-title{font-size:1.72rem !important;}
            .hero p,.hc-hero-sub{font-size:.94rem !important;}
            .hc-shell{padding:21px 19px;border-radius:13px;}
            [data-testid="stMetric"]{padding:14px;border-radius:11px;}
            [data-testid="stMetricValue"]{font-size:1.42rem;}
            [data-baseweb="tab-list"]{width:100%;overflow-x:auto;}
            .st-key-first_0 button,.st-key-first_1 button,.st-key-first_2 button,.st-key-first_3 button,
            .st-key-first_4 button,.st-key-first_5 button,.st-key-first_6 button,.st-key-first_7 button{min-height:54px !important;font-size:.85rem !important;}
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
    st.markdown(
        f'<div class="hc-insight"><b>{html.escape(title)}</b><br>{html.escape(body)}</div>',
        unsafe_allow_html=True,
    )
