import streamlit as st

def apply_styles():
    st.markdown("""<style>
    .block-container {max-width: 1500px; padding-top: 2rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {background: #142333; border: 1px solid #294658; border-radius: 12px; padding: 15px;}
    [data-testid="stMetricValue"] {font-size: clamp(1.2rem, 2vw, 2rem);}
    [data-testid="stSidebar"] {border-right: 1px solid #294658;}
    h1,h2,h3 {letter-spacing: -.025em;}
    .nexus-accent {color: #20d8d0;}
    </style>""", unsafe_allow_html=True)
