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
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap: .35rem;}
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
