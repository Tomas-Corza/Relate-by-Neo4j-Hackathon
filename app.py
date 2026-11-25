import pandas as pd
import streamlit as st
from graph import demo_graph, analyze, rows
from attribution import MODELS
from agent import investigate

st.set_page_config(page_title="OpenClaw Nexus",page_icon="🔗",layout="wide")
st.title("OpenClaw Nexus")
st.caption("Graph-powered marketing intelligence | Embedded Relate by Neo4j | Synthetic demonstration")
model=st.sidebar.selectbox("Attribution model",MODELS,index=2)
st.sidebar.caption("No live business accounts. No advertising actions. Attribution is not causal. Public AI requests share a limited quota; offline analytics remain available.")
question=st.text_input("Ask the graph","Which campaigns have inventory risks?",max_chars=500)
ask=st.button("Investigate",type="primary")
try:
    with demo_graph() as db:
        attribution,campaigns=analyze(db,model)
        totals=attribution["totals"]
        a,b,c=st.columns(3)
        a.metric("Revenue",f"${float(totals['total_revenue']):,.2f}")
        b.metric("Attributed revenue",f"${float(totals['attributed_revenue']):,.2f}")
        c.metric("Orders",totals["total_conversions"])
        if ask:
            try:
                answer,context=investigate(db,question,model)
                st.subheader("Analyst recommendation")
                st.write(answer)
                with st.expander("Evidence used"): st.json(context)
            except Exception as exc:
                st.error("Analyst request failed. Graph dashboard remains available.")
        t1,t2,t3=st.tabs(["Campaign economics","Customer journey","Inventory risk"])
        with t1:
            df=pd.DataFrame(campaigns)
            st.dataframe(df,hide_index=True,use_container_width=True)
            st.bar_chart(df.set_index("campaign")[["revenue","spend","gross_profit"]])
            st.caption("Spend is synthetic campaign-period spend; profit after ads excludes overhead and other costs.")
        with t2:
            uid=st.selectbox("Customer",[f"U{i:03}" for i in range(1,81)])
            journey=rows(db,"journey",{"customer":uid})
            orders=rows(db,"customer_orders",{"customer":uid})
            # IDs are generated internally; graph labels come from fixed synthetic values.
            dot=['digraph { rankdir=LR; node [shape=box]; customer [label="'+uid+'"];']
            for i,t in enumerate(journey):
                dot.append(f'customer -> t{i} [label="HAS_TOUCH"]; t{i} [label="{t["touchpoint"]}"]; t{i} -> c{i} [label="FROM_CAMPAIGN"]; c{i} [label="{t["campaign"]}"]; c{i} -> p{i} [label="PROMOTES"]; p{i} [label="{t["promoted_product"]}"];')
            for i,o in enumerate(orders):
                dot.append(f'customer -> o{i} [label="PLACED"]; o{i} [label="{o["order_id"]}"]; o{i} -> bought{i} [label="CONTAINS"]; bought{i} [label="{o["product"]}"];')
            st.graphviz_chart("\n".join(dot+["}"]))
            st.dataframe(journey,use_container_width=True)
            st.dataframe(orders,use_container_width=True)
        with t3:
            st.dataframe(rows(db,"risk"),use_container_width=True)
            st.warning("Review paid campaigns promoting products with fewer than 10 units. Human approval is required for any real-world action.")
        with st.expander("Attribution audit"):
            st.dataframe(attribution["conversions"])
except Exception as exc:
    st.error("Graph initialization or query failed. Contact the demo administrator.")
    st.stop()
