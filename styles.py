import streamlit as st

def apply_styles():
    st.markdown("""<style>
    .block-container {max-width: 1500px; padding-top: 5rem; padding-bottom: 2.5rem;}
    [data-testid="stAppViewContainer"] {background: #0b1420;}
    [data-testid="stHeader"] {background: #0b1420;}
    [data-testid="stSidebar"] {background: #101e2c; border-right: 1px solid #294658;}
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        justify-content: flex-start; text-align: left; border: 1px solid transparent;
        min-height: 2.45rem; padding: .35rem .7rem; border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {background: transparent; color: #d5e2ec;}
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {background: #16434b; color: #83f4ed; border-color: #24646a;}
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {border-color: #20d8d0;}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap: .22rem;}
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        display: flex !important; justify-content: flex-start !important;
        align-items: center !important; text-align: left !important;
        min-height: 2.4rem; padding: .35rem .75rem; gap: .65rem;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button > div {
        display: flex !important; width: 100%; justify-content: flex-start !important;
        align-items: center !important; text-align: left !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stButton"] button p {
        text-align: left !important; justify-content: flex-start !important; margin: 0;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"] {flex: 1; min-width: 0;}
    [data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stIconMaterial"] {flex: 0 0 1.2rem; width: 1.2rem; text-align: center;}
    .nexus-nav-heading {font-size: .69rem; font-weight: 700; letter-spacing: .11em; color: #91a6ba; margin: 1.15rem .75rem .45rem;}
    .nexus-sidebar-brand {display:flex; align-items:center; gap:.65rem; padding:.3rem 0 1.1rem;}
    .nexus-sidebar-brand img {width:44px; height:44px; object-fit:contain;}
    .nexus-sidebar-brand strong {font-size:1.05rem; color:#edf5fa; white-space:normal;}
    .nexus-sidebar-brand small {display:block; font-size:.65rem; letter-spacing:.08em; color:#91a6ba;}
    .nexus-header {display:flex; align-items:center; gap:1rem; padding:0 0 .25rem;}
    .nexus-header img {width:66px; height:66px; object-fit:contain; flex-shrink:0;}
    .nexus-header h1 {font-size:2.15rem; line-height:1.15; margin:.3rem 0; padding:0;}
    .nexus-header p {font-size:.84rem; color:#a9c0d0; margin:0;}
    @media (max-width:700px) {.nexus-header img {width:44px;height:44px;} .nexus-header h1 {font-size:1.65rem;}}
    [data-testid="stMetric"] {background: #142333; border: 1px solid #294658; border-radius: 12px; padding: 16px 18px; min-height: 105px;}
    [data-testid="stMetricLabel"] {color: #b8cad9;}
    [data-testid="stMetricValue"] {font-size: clamp(1.15rem, 2.1vw, 2rem); font-weight: 650; letter-spacing: -.035em;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-color: #294658; border-radius: 14px;}
    [data-testid="stExpander"] {border-color: #294658;}
    h1,h2,h3 {letter-spacing: -.025em;}
    .nexus-accent {color: #20d8d0;}
    .nexus-kicker {color: #82aabf; font-size: .76rem; font-weight: 650; letter-spacing: .12em; text-transform: uppercase;}
    .nexus-rule {height: 1px; background: linear-gradient(90deg,#20d8d0,#294658 35%,transparent); margin: .5rem 0 1rem;}
    [data-testid="stText"] {white-space: pre-wrap; overflow-wrap: anywhere;}
    [data-testid="stText"] pre {white-space: pre-wrap; overflow-wrap: anywhere;}
    @media (max-width: 700px) {
        .block-container {padding-left: 1rem; padding-right: 1rem; padding-top: 5rem;}
        [data-testid="stMetric"] {min-height: 80px; padding: 12px;}
    }
    </style>""", unsafe_allow_html=True)
