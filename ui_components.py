import os
import time
from pathlib import Path
import base64
import streamlit as st
import pandas as pd
import altair as alt
from graph import rows
from agent import investigate

LOGO = Path(__file__).parent / "assets" / "corza-logo.b64"

def brand():
    import io
    from PIL import Image
    logo = None
    try:
        if LOGO.exists():
            with Image.open(io.BytesIO(base64.b64decode(LOGO.read_text().strip()))) as im:
                logo = im.convert("RGBA")
    except Exception:
        pass
    if logo is not None:
        st.sidebar.image(logo, width=112)
    st.sidebar.markdown("**CORZA MARKETING**")
    left, right = st.columns([1, 8], vertical_alignment="center")
    with left:
        if logo is not None:
            st.image(logo, width=112)
        else:
            st.markdown("## CM")
    with right:
        st.markdown("**CORZA MARKETING  /  EXECUTIVE INTELLIGENCE**")
        st.markdown("# OpenClaw <span class='nexus-accent'>Nexus</span>", unsafe_allow_html=True)
        st.caption("A Corza Marketing product • Powered by Relate by Neo4j • Synthetic demo data")


def money(value):
    return f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"

def kpis(totals, campaigns):
    spend=sum(c["spend"] for c in campaigns)
    rev=float(totals["total_revenue"])
    attributed=float(totals["attributed_revenue"])
    profit=sum(c["profit_after_ads"] for c in campaigns)
    metrics=[("Revenue",money(rev)),("Attributed revenue",money(attributed)),("Orders",str(totals["total_conversions"])),("Campaign spend",money(spend)),("Blended revenue / spend",f"{rev/spend:.2f}x" if spend else "N/A"),("Attributed profit after ads",money(profit))]
    for col,(label,value) in zip(st.columns(3),metrics[:3]): col.metric(label,value)
    for col,(label,value) in zip(st.columns(3),metrics[3:]): col.metric(label,value)
    st.caption("Blended revenue / spend includes organic revenue; it is not paid-channel ROAS. Profit excludes overhead, taxes, shipping and returns.")

def campaign_chart(campaigns):
    df=pd.DataFrame(campaigns)
    long=df.melt(id_vars=["campaign"],value_vars=["revenue","gross_profit","spend"],var_name="metric",value_name="amount")
    chart=alt.Chart(long).mark_bar(cornerRadiusTopLeft=3,cornerRadiusTopRight=3).encode(
        x=alt.X("campaign:N",title=None,axis=alt.Axis(labelAngle=-20)),
        xOffset="metric:N",y=alt.Y("amount:Q",title="USD"),
        color=alt.Color("metric:N",scale=alt.Scale(domain=["revenue","gross_profit","spend"],range=["#20d8d0","#6689e8","#8394a6"]),title=None),
        tooltip=["campaign","metric",alt.Tooltip("amount:Q",format=",.2f")]).properties(height=280)
    st.altair_chart(chart,use_container_width=True)

def profit_chart(campaigns):
    chart=alt.Chart(pd.DataFrame(campaigns)).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y("campaign:N",sort="-x",title=None),x=alt.X("profit_after_ads:Q",title="USD"),
        color=alt.condition(alt.datum.profit_after_ads>=0,alt.value("#20d8d0"),alt.value("#ff7885")),
        tooltip=["campaign",alt.Tooltip("profit_after_ads:Q",format=",.2f")]).properties(height=280)
    st.altair_chart(chart,use_container_width=True)

def inventory(db):
    risks=rows(db,"risk")
    st.metric("Paid campaigns with low stock",len(risks))
    for r in risks:
        st.warning(f"{r['campaign_id']} · {r['product']} — {r['stock']} units; {money(r['spend'])} campaign spend")
    if not risks: st.success("No low-stock paid campaigns in this dataset.")
    st.caption("Risk threshold: fewer than 10 units. No stockout date predicted.")

def journeys(db):
    uid=st.selectbox("Customer",[f"U{i:03}" for i in range(1,81)])
    journey=rows(db,"journey",{"customer":uid})
    orders=rows(db,"customer_orders",{"customer":uid})
    st.caption("Customer (blue) • Touchpoint (gray) • Campaign (teal) • Product (amber) • Order (purple)")
    import json
    q=json.dumps
    dot=['digraph { rankdir=LR; node [shape=box,style="rounded,filled",fontcolor="#ffffff",color="#456075"]; customer [fillcolor="#365c91",label='+q(uid)+'];']
    for i,t in enumerate(journey):
        dot.append(f'customer -> t{i} [label="HAS_TOUCH"]; t{i} [fillcolor="#41566c",label={q(t["touchpoint"])}]; t{i} -> c{i} [label="FROM_CAMPAIGN"]; c{i} [fillcolor="#087c80",label={q(t["campaign"])}]; c{i} -> p{i} [label="PROMOTES"]; p{i} [fillcolor="#8a622a",label={q(t["promoted_product"])}];')
    for i,o in enumerate(orders):
        dot.append(f'customer -> o{i} [label="PLACED"]; o{i} [fillcolor="#6953a3",label={q(o["order_id"])}]; o{i} -> bought{i} [label="CONTAINS"]; bought{i} [fillcolor="#8a622a",label={q(o["product"])}];')
    st.graphviz_chart("\n".join(dot+["}"]))
    st.dataframe(journey,use_container_width=True,hide_index=True)
    st.dataframe(orders,use_container_width=True,hide_index=True)

def recommendations(campaigns, db):
    for r in rows(db,"risk"):
        st.warning(f"Review {r['campaign_id']} spend before replenishment: {r['stock']} units of {r['product']} remain.")
    paid=[c for c in campaigns if c["spend"]>0 and c["stock"]>=10]
    if paid:
        best=max(paid,key=lambda c:c["profit_after_ads"])
        st.info(f"Evaluate a controlled test for {best['campaign_id']} {best['campaign']}: attributed profit after ads {money(best['profit_after_ads'])}. Historical performance does not predict marginal returns.")
    st.caption("Rule-based suggestions; no budget changes executed.")

def analyst(db,model):
    st.caption("AI configured" if os.getenv("OPENAI_API_KEY") else "Offline analyst mode")
    st.caption("A configured key does not guarantee provider availability. Shared quotas apply. Questions may be sent to OpenAI; do not enter personal or confidential information.")
    prompts=["Which campaigns have inventory risks?","Compare campaign profitability and suggest a controlled budget test.","Explain the customer journey for U001.","What are the limitations of this attribution model?"]
    chosen=st.selectbox("Suggested questions",prompts)
    question=st.text_area("Ask the graph",value=chosen,max_chars=500,key="ask_"+str(prompts.index(chosen)))
    if st.button("Investigate",type="primary"):
        try:
            now=time.monotonic()
            if now-st.session_state.get("nexus_last_request",-1000000)<15:
                st.warning("Please wait 15 seconds between analyst requests.")
                return
            st.session_state["nexus_last_request"]=now
            with st.spinner("Analyzing graph evidence…"):
                answer,context=investigate(db,question,model)
            st.session_state["nexus_answer"]=(answer,context,question,model)
        except Exception:
            st.error("Analyst request failed. Graph dashboard remains available.")
    if "nexus_answer" in st.session_state:
        answer,context,asked,used_model=st.session_state["nexus_answer"]
        st.caption(f"Last analysis • {used_model} • {asked}")
        st.text(answer)
        with st.expander("Evidence used"): st.json(context)
