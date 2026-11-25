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
    logo_html = ""
    try:
        if LOGO.exists():
            with Image.open(io.BytesIO(base64.b64decode(LOGO.read_text().strip()))) as im:
                buffer = io.BytesIO()
                im.convert("RGBA").save(buffer, format="PNG")
                encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
                logo_html = f'<img src="data:image/png;base64,{encoded}" alt="Corza Marketing logo">'
    except Exception:
        pass
    st.sidebar.markdown(
        f'<div class="nexus-sidebar-brand">{logo_html}<div><strong>OpenClaw <span class="nexus-accent">Nexus</span></strong><small>BY CORZA MARKETING</small></div></div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div class="nexus-header">{logo_html}<div><div class="nexus-kicker">Corza Marketing / Executive intelligence</div><h1>OpenClaw <span class="nexus-accent">Nexus</span></h1><p>Powered by Relate by Neo4j · Synthetic demo data</p></div></div><div class="nexus-rule"></div>',
        unsafe_allow_html=True)


def navigation():
    groups = [
        ("OVERVIEW", [("Executive dashboard", "dashboard"), ("Campaigns", "campaign"), ("Attribution", "pie_chart"), ("Profitability", "payments")]),
        ("INTELLIGENCE", [("Inventory", "inventory_2"), ("Customers", "group"), ("Graph intelligence", "hub"), ("Budget simulator", "tune"), ("AI insights", "auto_awesome")]),
        ("WORKSPACE", [("Reports", "description")]),
    ]
    if "nexus_page" not in st.session_state:
        st.session_state["nexus_page"] = "Executive dashboard"
    for heading, entries in groups:
        st.sidebar.markdown(f'<div class="nexus-nav-heading">{heading}</div>', unsafe_allow_html=True)
        for label, icon in entries:
            st.sidebar.button(label, icon=f":material/{icon}:", key="nav_"+label,
                type="primary" if st.session_state["nexus_page"] == label else "secondary",
                use_container_width=True, on_click=_navigate, args=(label,))
    st.sidebar.divider()
    return st.session_state["nexus_page"]

def _navigate(label):
    st.session_state["nexus_page"] = label

def campaign_table(campaigns):
    df = pd.DataFrame(campaigns)
    st.dataframe(df, hide_index=True, use_container_width=True, column_config={
        "campaign_id": "ID", "campaign": "Campaign", "channel": "Channel",
        "product": "Promoted product", "stock": st.column_config.NumberColumn("Stock", format="%d"),
        "spend": st.column_config.NumberColumn("Spend", format="dollar"),
        "revenue": st.column_config.NumberColumn("Attributed revenue", format="dollar"),
        "gross_profit": st.column_config.NumberColumn("Attributed gross profit", format="dollar"),
        "profit_after_ads": st.column_config.NumberColumn("Profit after ads", format="dollar"),
        "roas": st.column_config.NumberColumn("ROAS", format="%.2fx"),
    })

def polish_chart(chart):
    return chart.configure_view(strokeOpacity=0).configure_axis(
        labelColor="#c2d3e1", titleColor="#a9c0d0", gridColor="#294052",
        domain=False, tickColor="#294052", labelFontSize=12
    ).configure_legend(labelColor="#c2d3e1", titleColor="#a9c0d0",
        orient="top", labelFontSize=12).configure(background="transparent")

def money(value):
    return f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"

def kpis(totals, campaigns):
    st.subheader("Performance overview")
    st.caption("Campaign-period results · Synthetic business dataset")
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
    long["metric"]=long["metric"].map({"revenue":"Attributed revenue","gross_profit":"Gross profit","spend":"Campaign spend"})
    chart=alt.Chart(long).mark_bar(cornerRadiusTopLeft=3,cornerRadiusTopRight=3).encode(
        x=alt.X("campaign:N",title=None,axis=alt.Axis(labelAngle=-20)),
        xOffset="metric:N",y=alt.Y("amount:Q",title="USD",axis=alt.Axis(format="$,.0f")),
        color=alt.Color("metric:N",scale=alt.Scale(domain=["Attributed revenue","Gross profit","Campaign spend"],range=["#20d8d0","#6689e8","#8394a6"]),title=None),
        tooltip=["campaign","metric",alt.Tooltip("amount:Q",format="$,.2f")]).properties(height=280)
    st.altair_chart(polish_chart(chart),use_container_width=True)

def profit_chart(campaigns):
    chart=alt.Chart(pd.DataFrame(campaigns)).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y("campaign:N",sort="-x",title=None),x=alt.X("profit_after_ads:Q",title="USD"),
        color=alt.condition(alt.datum.profit_after_ads>=0,alt.value("#20d8d0"),alt.value("#ff7885")),
        tooltip=["campaign",alt.Tooltip("profit_after_ads:Q",format=",.2f")]).properties(height=280)
    st.altair_chart(polish_chart(chart),use_container_width=True)

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
        with st.container(border=True):
            st.markdown("**Analyst response**")
            st.text(answer)
        with st.expander("Evidence used"): st.json(context)
