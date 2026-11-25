import pandas as pd
import streamlit as st
from graph import demo_graph, analyze, rows
from attribution import MODELS
from styles import apply_styles
from advanced_views import graph_view, customer_view, model_view, budget_view
from ui_components import brand,kpis,campaign_chart,profit_chart,inventory,journeys,recommendations,analyst

st.set_page_config(page_title="OpenClaw Nexus",page_icon="🔗",layout="wide")
apply_styles()
brand()
page=st.sidebar.radio("Navigation",["Executive dashboard","Campaigns","Attribution","Profitability","Inventory","Customers","Graph intelligence","Budget simulator","AI insights","Reports"])
model=st.sidebar.selectbox("Attribution model",MODELS,index=2)
st.sidebar.caption("Synthetic data only. No advertising actions. Attribution is descriptive, not causal. Public AI quota is shared.")
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
            st.dataframe(campaigns,hide_index=True,use_container_width=True)
        elif page=="Attribution":
            st.subheader("Attribution audit")
            st.json(attribution["totals"])
            st.dataframe(attribution["channels"],hide_index=True,use_container_width=True)
            st.dataframe(attribution["conversions"],hide_index=True,use_container_width=True)
            with st.expander("Touchpoint allocations"): st.dataframe(attribution["allocations"])
            model_view(db)
        elif page=="Profitability":
            st.subheader("Attributed gross profit less campaign spend")
            profit_chart(campaigns)
            st.dataframe(campaigns,hide_index=True,use_container_width=True)
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
            st.subheader("Export synthetic analytics")
            st.download_button("Campaign report CSV",pd.DataFrame(campaigns).to_csv(index=False),"campaigns.csv","text/csv")
            st.download_button("Attribution audit CSV",pd.DataFrame(attribution["conversions"]).to_csv(index=False),"attribution.csv","text/csv")
        st.caption("OpenClaw Nexus · Corza Marketing · Relate by Neo4j Hackathon")
except Exception:
    st.error("Dashboard could not load. Contact the demo administrator.")
    st.stop()
