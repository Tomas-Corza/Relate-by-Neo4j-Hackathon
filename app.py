from decimal import Decimal
import pandas as pd
import streamlit as st
from graph import demo_graph, analyze, rows
from attribution import MODELS
from styles import apply_styles
from advanced_views import graph_view, customer_view, model_view, budget_view
from ui_components import brand,kpis,campaign_chart,profit_chart,inventory,journeys,recommendations,analyst,navigation,campaign_table

st.set_page_config(page_title="OpenClaw Nexus",page_icon="🔗",layout="wide")
apply_styles()
brand()
page=navigation()
model=st.sidebar.selectbox("Attribution model",MODELS,index=2)
st.sidebar.caption("Synthetic demo environment · No live accounts")
st.sidebar.caption("Attribution is descriptive, not causal. Public AI quota is shared.")
try:
    with demo_graph() as db:
        attribution,campaigns=analyze(db,model)
        if page=="Executive dashboard":
            kpis(attribution["totals"],campaigns)
            left,right=st.columns([1.2,1])
            with left:
                with st.container(border=True):
                    st.subheader("Campaign performance")
                    campaign_chart(campaigns)
            with right:
                with st.container(border=True):
                    st.subheader("Profitability comparison")
                    profit_chart(campaigns)
            a,b,c=st.columns(3)
            with a:
                with st.container(border=True):
                    st.subheader("Inventory risk")
                    inventory(db)
            with b:
                with st.container(border=True):
                    st.subheader("Customer journey")
                    orders=rows(db,"orders")
                    touches=rows(db,"touches")
                    counts=pd.Series([o["customer_id"] for o in orders]).value_counts()
                    st.metric("Purchasing customers",len(counts))
                    st.metric("Repeat customers",int((counts>1).sum()))
                    st.metric("Recorded touchpoints",len(touches))
                    st.caption("Explore individual paths in Customers.")
            with c:
                with st.container(border=True):
                    st.subheader("Recommended reviews")
                    recommendations(campaigns,db)
            with st.container(border=True):
                st.subheader("AI analyst")
                analyst(db,model)
        elif page=="Campaigns":
            st.subheader("Campaign economics")
            campaign_chart(campaigns)
            campaign_table(campaigns)
        elif page=="Attribution":
            st.subheader("Attribution audit")
            st.caption("Revenue reconciliation and attribution integrity")
            totals=attribution["totals"]
            metrics=[
                ("Total conversions", totals["total_conversions"]),
                ("Attributed conversions", totals["attributed_conversions"]),
                ("Unattributed conversions", totals["unattributed_conversions"]),
                ("Total revenue", f"${Decimal(totals['total_revenue']):,.2f}"),
                ("Attributed revenue", f"${Decimal(totals['attributed_revenue']):,.2f}"),
                ("Unattributed revenue", f"${Decimal(totals['unattributed_revenue']):,.2f}"),
            ]
            for group in (metrics[:3],metrics[3:]):
                for col,(label,value) in zip(st.columns(3),group):
                    col.metric(label,value)
            revenue=Decimal(totals["total_revenue"])
            allocated=Decimal(totals["attributed_revenue"])
            unallocated=Decimal(totals["unattributed_revenue"])
            with st.container(border=True):
                st.markdown("**Revenue attribution coverage**")
                if revenue>0:
                    coverage=float(allocated/revenue)
                    st.metric("Share of revenue attributed",f"{coverage:.1%}")
                    st.progress(max(0.0,min(1.0,coverage)))
                else:
                    st.caption("Coverage is undefined when total revenue is zero or negative.")
                if allocated+unallocated!=revenue:
                    st.error("Revenue reconciliation mismatch. Review the audit records.")
                elif unallocated==0 and allocated==revenue:
                    st.success("Revenue reconciles with no unattributed balance.")
                else:
                    st.info("Revenue reconciles, including the unattributed balance.")
                st.caption("Coverage measures allocation completeness, not attribution accuracy or causal lift.")
            st.subheader("Channel attribution")
            st.dataframe(attribution["channels"],hide_index=True,use_container_width=True)
            model_view(db)
            with st.expander("Conversion-level audit"):
                st.dataframe(attribution["conversions"],hide_index=True,use_container_width=True)
            with st.expander("Touchpoint allocations"):
                st.dataframe(attribution["allocations"],hide_index=True,use_container_width=True)
            with st.expander("Technical audit — raw JSON"):
                st.json(totals)
        elif page=="Profitability":
            st.subheader("Attributed gross profit less campaign spend")
            profit_chart(campaigns)
            campaign_table(campaigns)
            st.caption("Excludes overhead, taxes, shipping and returns.")
        elif page=="Inventory":
            st.subheader("Inventory risk")
            inventory(db)
            st.dataframe(rows(db,"campaigns"),hide_index=True,use_container_width=True)
        elif page=="Customers":
            st.subheader("Graph-powered customer journeys")
            customer_view(db)
            journeys(db)
        elif page=="Graph intelligence":
            graph_view(db)
        elif page=="Budget simulator":
            budget_view(campaigns)
        elif page=="AI insights":
            st.subheader("Graph evidence and AI analysis")
            recommendations(campaigns,db)
            analyst(db,model)
        elif page=="Reports":
            st.subheader("Reporting workspace")
            st.caption("Export auditable campaign and conversion records for independent analysis.")
            st.download_button("Campaign report CSV",pd.DataFrame(campaigns).to_csv(index=False),"campaigns.csv","text/csv")
            st.download_button("Attribution audit CSV",pd.DataFrame(attribution["conversions"]).to_csv(index=False),"attribution.csv","text/csv")
        st.caption("OpenClaw Nexus · Corza Marketing · Relate by Neo4j Hackathon")
except Exception:
    st.error("Dashboard could not load. Contact the demo administrator.")
    st.stop()
