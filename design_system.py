from __future__ import annotations

import html

import streamlit as st


ACCENT = "#4F5DFF"
INK = "#10131A"
MUTED = "#697386"
SURFACE = "#FFFFFF"
SOFT = "#F6F7FB"
BORDER = "#E7E9F0"
POSITIVE = "#0F9F75"
WARNING = "#B76B10"
DANGER = "#D64545"


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root{
          --cp-accent:#4F5DFF;
          --cp-accent-2:#6C47FF;
          --cp-accent-soft:#EEF0FF;
          --cp-ink:#10131A;
          --cp-muted:#697386;
          --cp-subtle:#98A1B2;
          --cp-bg:#F6F7FB;
          --cp-surface:#FFFFFF;
          --cp-surface-2:#FBFBFD;
          --cp-border:#E7E9F0;
          --cp-border-strong:#D8DCE7;
          --cp-positive:#0F9F75;
          --cp-warning:#B76B10;
          --cp-danger:#D64545;
          --cp-sidebar:#11151D;
          --cp-sidebar-2:#171C25;
          --cp-shadow:0 1px 2px rgba(16,19,26,.04),0 14px 38px rgba(16,19,26,.055);
          --cp-shadow-soft:0 1px 2px rgba(16,19,26,.035),0 8px 22px rgba(16,19,26,.035);
        }

        html,body,[class*="css"]{
          font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif;
          font-feature-settings:"tnum" 1,"cv11" 1;
          -webkit-font-smoothing:antialiased;
          text-rendering:optimizeLegibility;
        }
        .stApp{
          color:var(--cp-ink);
          background:
            radial-gradient(900px 480px at 86% -120px,rgba(79,93,255,.08),transparent 64%),
            radial-gradient(720px 420px at 16% 105%,rgba(83,214,177,.05),transparent 62%),
            var(--cp-bg);
        }
        .block-container{max-width:1380px!important;padding:1.65rem 2rem 5rem!important;}
        footer,[data-testid="stDecoration"]{display:none!important;}
        [data-testid="stHeader"]{
          background:rgba(246,247,251,.76)!important;
          backdrop-filter:blur(18px) saturate(1.25);
          border-bottom:1px solid rgba(231,233,240,.58);
        }
        [data-testid="stToolbarActions"]{display:none!important;}
        [data-testid="stSidebarNav"]{display:none!important;}
        [data-testid="stSidebar"] [role="radiogroup"]{display:none!important;}
        [data-testid="stSidebar"] [data-testid="stAlert"]{display:none!important;}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"]{display:none!important;}

        /* ----- Product navigation ----- */
        [data-testid="stSidebar"]{
          width:268px!important;min-width:268px!important;
          background:
            radial-gradient(420px 260px at 12% -10%,rgba(79,93,255,.18),transparent 72%),
            linear-gradient(180deg,var(--cp-sidebar),#0E1219 78%)!important;
          border-right:1px solid rgba(255,255,255,.055)!important;
        }
        [data-testid="stSidebar"]>div:first-child{padding:1.15rem .82rem 1.1rem!important;overflow-y:auto;}
        [data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.07);margin:1rem .28rem;}
        [data-testid="stSidebar"] a{text-decoration:none!important;}
        .cp-brand{display:flex;align-items:center;gap:11px;padding:5px 8px 22px;}
        .cp-brand-mark{
          width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;
          color:#fff;font-weight:820;font-size:.75rem;letter-spacing:-.03em;
          background:linear-gradient(145deg,#6672FF,#4F5DFF 58%,#7A4DFF);
          box-shadow:0 8px 26px rgba(79,93,255,.30),inset 0 1px 0 rgba(255,255,255,.28);
        }
        .cp-brand-title{font-size:1rem;font-weight:760;letter-spacing:-.025em;color:#F8FAFC;line-height:1.05;}
        .cp-brand-sub{font-size:.66rem;line-height:1.2;color:#7F899B;margin-top:5px;letter-spacing:.095em;text-transform:uppercase;font-weight:680;}
        .cp-nav-section{font-size:.61rem;text-transform:uppercase;letter-spacing:.14em;font-weight:760;color:#667084;margin:18px 10px 7px;}
        .cp-nav-link{
          display:flex;align-items:center;gap:10px;min-height:43px;padding:9px 10px;margin:2px 0;border-radius:11px;
          color:#B9C1D0!important;font-size:.865rem;font-weight:570;line-height:1.18;border:1px solid transparent;
          transition:background .16s ease,border-color .16s ease,color .16s ease,transform .16s ease;
        }
        .cp-nav-link svg{width:17px;height:17px;stroke:#778297;flex:none;transition:stroke .16s ease,transform .16s ease;}
        .cp-nav-link:hover{background:rgba(255,255,255,.055);color:#F8FAFC!important;transform:translateX(1px);}
        .cp-nav-link:hover svg{stroke:#AEB9CD;}
        .cp-nav-link.active{
          color:#fff!important;font-weight:680;background:linear-gradient(90deg,rgba(79,93,255,.22),rgba(79,93,255,.10));
          border-color:rgba(121,132,255,.20);box-shadow:inset 3px 0 0 #6E79FF;
        }
        .cp-nav-link.active svg{stroke:#94A0FF;}
        .cp-nav-link.cta{
          background:#F7F8FC;color:#171B24!important;font-weight:720;margin:2px 0 15px;
          box-shadow:0 6px 18px rgba(0,0,0,.16),inset 0 1px 0 #fff;border-color:#fff;
        }
        .cp-nav-link.cta svg{stroke:#4F5DFF;}
        .cp-nav-link.cta:hover{background:#fff;color:#10131A!important;transform:translateY(-1px);}
        .cp-sidebar-note{font-size:.69rem;line-height:1.48;color:#687386;padding:12px 10px 3px;}
        .cp-soon{padding:8px 10px;color:#66758A;font-size:.82rem;display:flex;align-items:center;gap:9px;}
        .cp-soon:before{content:"";width:6px;height:6px;border-radius:50%;background:#394151;flex:none;}

        /* ----- Type hierarchy ----- */
        h1,h2,h3{color:var(--cp-ink);letter-spacing:-.038em;}
        h1{font-size:2.15rem!important;font-weight:760!important;line-height:1.08!important;}
        h2{font-size:1.34rem!important;font-weight:720!important;line-height:1.18!important;}
        h3{font-size:1.04rem!important;font-weight:690!important;line-height:1.28!important;}
        p,.stCaption{color:var(--cp-muted);}
        .stCaption{line-height:1.45;}

        /* ----- Buttons ----- */
        .stButton>button,.stFormSubmitButton>button,.stLinkButton>a,.stDownloadButton>button{
          min-height:46px!important;border-radius:12px!important;padding:.58rem 1.02rem!important;
          font-size:.875rem!important;font-weight:680!important;letter-spacing:-.008em!important;
          box-shadow:none!important;transition:background .16s ease,border-color .16s ease,box-shadow .16s ease,transform .14s ease!important;
        }
        .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stLinkButton>a[kind="primary"]{
          color:#fff!important;border:1px solid #4F5DFF!important;
          background:linear-gradient(135deg,#5865FF 0%,#4F5DFF 56%,#6A4EFF 100%)!important;
          box-shadow:0 8px 20px rgba(79,93,255,.20)!important;
        }
        .stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover,.stLinkButton>a[kind="primary"]:hover{
          border-color:#4653EB!important;background:linear-gradient(135deg,#4E5AF2,#4653E9 58%,#6043F0)!important;
          box-shadow:0 11px 27px rgba(79,93,255,.27)!important;transform:translateY(-1px);
        }
        .stButton>button[kind="secondary"],.stLinkButton>a[kind="secondary"],.stDownloadButton>button{
          background:#fff!important;border:1px solid var(--cp-border-strong)!important;color:#242A36!important;
          box-shadow:0 1px 2px rgba(16,19,26,.025)!important;
        }
        .stButton>button[kind="secondary"]:hover,.stLinkButton>a[kind="secondary"]:hover,.stDownloadButton>button:hover{
          background:#FBFBFE!important;border-color:#C9CEDB!important;color:#10131A!important;transform:translateY(-1px);
          box-shadow:0 5px 14px rgba(16,19,26,.055)!important;
        }
        .stButton>button:active,.stFormSubmitButton>button:active,.stLinkButton>a:active{transform:translateY(0)!important;}
        .stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stLinkButton>a:focus-visible,.stDownloadButton>button:focus-visible{
          outline:3px solid rgba(79,93,255,.18)!important;outline-offset:2px!important;
        }

        /* Homepage choice tiles: deliberate, not generic buttons. */
        .st-key-first_0 button,.st-key-first_1 button,.st-key-first_2 button,.st-key-first_3 button,
        .st-key-first_4 button,.st-key-first_5 button,.st-key-first_6 button,.st-key-first_7 button{
          min-height:70px!important;justify-content:flex-start!important;text-align:left!important;padding:.9rem 1.05rem!important;
          color:#242A36!important;background:rgba(255,255,255,.92)!important;border:1px solid #E2E5EC!important;
          border-radius:15px!important;font-weight:665!important;box-shadow:0 1px 2px rgba(16,19,26,.025)!important;
        }
        .st-key-first_0 button:hover,.st-key-first_1 button:hover,.st-key-first_2 button:hover,.st-key-first_3 button:hover,
        .st-key-first_4 button:hover,.st-key-first_5 button:hover,.st-key-first_6 button:hover,.st-key-first_7 button:hover{
          color:#323AC4!important;background:#F6F7FF!important;border-color:#C8CDFF!important;
          box-shadow:0 10px 26px rgba(79,93,255,.09)!important;transform:translateY(-2px);
        }

        /* ----- Inputs / forms ----- */
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="textarea"]>div{
          min-height:46px;background:#fff!important;border:1px solid #DDE1EA!important;border-radius:12px!important;
          box-shadow:0 1px 2px rgba(16,19,26,.02)!important;transition:border-color .15s ease,box-shadow .15s ease!important;
        }
        [data-baseweb="input"]>div:focus-within,[data-baseweb="select"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within{
          border-color:#9EA7FF!important;box-shadow:0 0 0 3px rgba(79,93,255,.10)!important;
        }
        [data-testid="stFileUploader"] section{
          border:1px dashed #C8CEDB!important;border-radius:14px!important;background:#FBFBFD!important;
        }
        [data-testid="stExpander"]{
          background:rgba(255,255,255,.92);border:1px solid var(--cp-border);border-radius:14px!important;
          overflow:hidden;box-shadow:0 1px 2px rgba(16,19,26,.02);
        }
        [data-testid="stDataFrame"]{
          background:#fff;border:1px solid var(--cp-border);border-radius:14px;overflow:hidden;box-shadow:var(--cp-shadow-soft);
        }

        /* ----- Metrics / bento surfaces ----- */
        [data-testid="stMetric"]{
          position:relative;overflow:hidden;background:rgba(255,255,255,.96);border:1px solid var(--cp-border);
          border-radius:16px;padding:19px 19px 17px;box-shadow:var(--cp-shadow-soft);min-height:118px;
          transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;
        }
        [data-testid="stMetric"]:before{
          content:"";position:absolute;left:0;top:0;width:100%;height:3px;
          background:linear-gradient(90deg,#4F5DFF,#7B5CFA 58%,#69B7FF);opacity:.78;
        }
        [data-testid="stMetric"]:hover{transform:translateY(-2px);border-color:#D9DDF0;box-shadow:0 12px 30px rgba(16,19,26,.07);}
        [data-testid="stMetricLabel"]{font-size:.745rem;color:#737D8F;font-weight:630;letter-spacing:.012em;}
        [data-testid="stMetricValue"]{font-size:1.78rem;color:#10131A;font-weight:770;letter-spacing:-.05em;line-height:1.12;margin-top:4px;}
        [data-testid="stMetricDelta"]{font-size:.73rem;margin-top:5px;}

        /* ----- Tabs ----- */
        [data-baseweb="tab-list"]{
          display:flex;gap:3px;background:rgba(236,238,244,.84);border:1px solid #E0E3EA;border-radius:13px;padding:4px;
          width:max-content;max-width:100%;backdrop-filter:blur(8px);
        }
        [data-baseweb="tab"]{border-radius:10px;padding:.53rem .88rem;font-size:.835rem;font-weight:630;color:#70798A;min-height:38px;}
        [data-baseweb="tab"][aria-selected="true"]{
          background:#fff!important;color:#161A22!important;box-shadow:0 2px 7px rgba(16,19,26,.08);font-weight:690;
        }
        [data-baseweb="tab-highlight"]{display:none;}

        /* ----- Public landing hero ----- */
        .hero{
          color:#fff!important;position:relative;overflow:hidden;margin:3px 0 22px!important;padding:46px 46px 44px!important;
          border:1px solid rgba(255,255,255,.08)!important;border-radius:24px!important;
          background:
            radial-gradient(520px 300px at 89% 0%,rgba(104,115,255,.48),transparent 70%),
            radial-gradient(380px 250px at 15% 105%,rgba(27,176,145,.20),transparent 70%),
            linear-gradient(130deg,#121722 0%,#171D2C 56%,#1D2340 100%)!important;
          box-shadow:0 24px 70px rgba(22,27,43,.17)!important;
        }
        .hero:before{
          content:"";position:absolute;inset:0;pointer-events:none;opacity:.22;
          background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);
          background-size:36px 36px;mask-image:linear-gradient(to bottom,black,transparent 75%);
        }
        .hero:after{
          content:"";position:absolute;width:290px;height:290px;right:-95px;bottom:-180px;border-radius:42%;
          border:1px solid rgba(255,255,255,.12);transform:rotate(24deg);box-shadow:0 0 0 34px rgba(255,255,255,.025),0 0 0 72px rgba(255,255,255,.018);
        }
        .hero h1{position:relative;z-index:1;font-size:2.62rem!important;line-height:1.03!important;letter-spacing:-.055em!important;color:#fff!important;max-width:860px;margin:0 0 14px!important;font-weight:760!important;}
        .hero p{position:relative;z-index:1;font-size:1.02rem!important;line-height:1.65!important;color:#B7C0D2!important;max-width:740px;margin:0!important;}
        .answer-card,.finance-callout,.insight{
          background:linear-gradient(135deg,#F5F6FF,#FAFAFF)!important;border:1px solid #DBDEFF!important;
          border-radius:15px!important;color:#363F69!important;box-shadow:0 4px 16px rgba(79,93,255,.045)!important;
        }
        .demo-banner,.beta-note{background:#FFFAF0!important;border:1px solid #F0DFC1!important;border-radius:12px!important;color:#6D5425!important;}
        .module-card,.kpi{
          background:#fff!important;border:1px solid var(--cp-border)!important;border-radius:16px!important;
          box-shadow:0 1px 2px rgba(16,19,26,.025),0 8px 22px rgba(16,19,26,.035)!important;
        }
        .module-card{padding:20px!important;min-height:116px!important;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;}
        .module-card:hover{transform:translateY(-2px);border-color:#D8DCF0!important;box-shadow:0 14px 30px rgba(16,19,26,.065)!important;}
        .kpi{padding:19px!important;}
        .kpi .label{color:#737D8F!important;font-weight:630;}
        .kpi .value{color:#10131A!important;letter-spacing:-.045em;}

        /* ----- Private workspace shell ----- */
        .hc-shell{
          position:relative;overflow:hidden;background:
            radial-gradient(420px 190px at 96% -20%,rgba(79,93,255,.10),transparent 72%),
            linear-gradient(145deg,#fff,#FCFCFF);
          border:1px solid var(--cp-border);border-radius:20px;padding:30px 32px;box-shadow:var(--cp-shadow);margin-bottom:20px;
        }
        .hc-shell:after{content:"";position:absolute;width:150px;height:150px;right:-92px;top:-78px;border:1px solid rgba(79,93,255,.12);border-radius:36%;transform:rotate(24deg);}
        .hc-eyebrow{font-size:.66rem;font-weight:790;text-transform:uppercase;letter-spacing:.145em;color:#4F5DFF;margin-bottom:9px;}
        .hc-hero-title{font-size:2.18rem;line-height:1.06;letter-spacing:-.052em;font-weight:770;color:#10131A;max-width:900px;margin:0 0 11px;}
        .hc-hero-sub{font-size:.98rem;line-height:1.64;color:#697386;max-width:780px;margin:0;}
        .hc-section-title{font-size:1.02rem;font-weight:720;color:#202530;margin:28px 0 3px;letter-spacing:-.024em;}
        .hc-section-sub{font-size:.81rem;color:#7C8596;margin-bottom:12px;line-height:1.48;}
        .hc-card{background:#fff;border:1px solid var(--cp-border);border-radius:16px;padding:20px;box-shadow:var(--cp-shadow-soft);}
        .hc-card-label{font-size:.72rem;color:#7A8495;margin-bottom:7px;font-weight:640;}
        .hc-card-value{font-size:1.76rem;line-height:1.04;font-weight:770;letter-spacing:-.047em;color:#10131A;}
        .hc-card-note{font-size:.76rem;color:#697386;margin-top:8px;line-height:1.42;}
        .hc-insight{
          position:relative;background:linear-gradient(135deg,#F3F4FF,#F9F9FF);border:1px solid #DCDDFF;border-radius:15px;
          padding:17px 18px 17px 20px;margin:12px 0 18px;color:#3B446B;line-height:1.55;box-shadow:0 4px 16px rgba(79,93,255,.04);
        }
        .hc-insight:before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:3px;border-radius:8px;background:#5D68FF;}
        .hc-insight b{color:#343EC5;}
        .hc-warning{background:#FFF8EC;border:1px solid #F0DFC2;border-radius:14px;padding:15px 17px;color:#6C4D1B;margin:12px 0;}
        .hc-positive{background:#EFF9F5;border:1px solid #CFE9DF;border-radius:14px;padding:15px 17px;color:#285E4D;margin:12px 0;}
        .hc-pill{
          display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;background:#F0F1F6;border:1px solid #E3E5EC;
          color:#596274;font-size:.7rem;font-weight:660;
        }
        .hc-login-wrap{max-width:540px;margin:2rem auto 0;}
        .hc-login-card{background:#fff;border:1px solid var(--cp-border);border-radius:20px;padding:30px;box-shadow:var(--cp-shadow);}
        .hc-logo{display:inline-flex;width:44px;height:44px;border-radius:14px;align-items:center;justify-content:center;background:#4F5DFF;color:white;font-weight:820;margin-bottom:18px;box-shadow:0 9px 25px rgba(79,93,255,.22);}
        .hc-small{font-size:.76rem;color:#929BAC;}
        .hc-divider{height:1px;background:#ECEEF3;margin:19px 0;}

        /* Alerts */
        [data-testid="stAlert"]{border-radius:14px!important;border-width:1px!important;}

        /* Subtle entry motion: quick, not theatrical. */
        @keyframes cpRise{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
        .hero,.hc-shell,[data-testid="stMetric"]{animation:cpRise .32s cubic-bezier(.2,.8,.2,1) both;}
        @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}

        /* ----- Mobile ----- */
        @media(max-width:768px){
          .block-container{padding:1rem .9rem 4rem!important;max-width:100%!important;}
          [data-testid="stSidebar"]{width:min(86vw,318px)!important;min-width:min(86vw,318px)!important;}
          [data-testid="stSidebar"]>div:first-child{padding:.95rem .7rem 1rem!important;}
          .cp-brand{padding:4px 7px 16px;}
          .cp-nav-link{min-height:44px;border-radius:10px;}
          .cp-nav-secondary{display:none!important;}
          .hero{padding:30px 24px 29px!important;border-radius:20px!important;margin-top:0!important;}
          .hero h1{font-size:2.02rem!important;line-height:1.04!important;}
          .hero p{font-size:.93rem!important;line-height:1.55!important;}
          .hc-shell{padding:23px 21px;border-radius:17px;}
          .hc-hero-title{font-size:1.78rem;}
          .hc-hero-sub{font-size:.91rem;}
          [data-testid="stMetric"]{min-height:105px;padding:16px 16px 14px;border-radius:14px;}
          [data-testid="stMetricValue"]{font-size:1.52rem;}
          [data-baseweb="tab-list"]{width:100%;overflow-x:auto;justify-content:flex-start;}
          .st-key-first_0 button,.st-key-first_1 button,.st-key-first_2 button,.st-key-first_3 button,
          .st-key-first_4 button,.st-key-first_5 button,.st-key-first_6 button,.st-key-first_7 button{min-height:62px!important;}
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
    subtitle_html = f'<div class="hc-section-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="hc-section-title">{html.escape(title)}</div>{subtitle_html}',
        unsafe_allow_html=True,
    )


def insight(title: str, body: str) -> None:
    st.markdown(
        f'<div class="hc-insight"><b>{html.escape(title)}</b><br>{html.escape(body)}</div>',
        unsafe_allow_html=True,
    )
