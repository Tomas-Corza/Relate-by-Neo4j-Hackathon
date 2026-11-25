import streamlit as st
import pandas as pd
import altair as alt
from graph import rows, QUERIES
from intelligence import graph_counts, customer_value, path_insights, compare_models, scenario
from ui_components import money, polish_chart

def graph_view(db):
    st.subheader("Graph intelligence | Relate by Neo4j")
    st.caption("Live counts from the embedded graph. The same relationship paths feed the attribution engine and analyst.")
    nodes,edges=graph_counts(db)
    for col,(name,count) in zip(st.columns(5),nodes.items()): col.metric(name,count)
    st.metric("Stored relationships",sum(edges.values()))
    st.graphviz_chart('''digraph { rankdir=LR; node [shape=box,style=filled,fillcolor="#15485b",fontcolor=white];
    Customer -> Touchpoint [label="HAS_TOUCH"]; Touchpoint -> Campaign [label="FROM_CAMPAIGN"];
    Campaign -> Product [label="PROMOTES"]; Customer -> Order [label="PLACED"]; Order -> Product [label="CONTAINS"]; }''')
    st.dataframe([{"relationship":k,"count":v} for k,v in edges.items()],hide_index=True,use_container_width=True)
    st.subheader("Graph evidence explorer")
    st.caption("Choose a business question to inspect the results of a read-only query against Relate.")
    query_labels={
        "campaigns":"Campaigns and promoted products",
        "touches":"Customer marketing touchpoints",
        "orders":"Customer orders and product economics",
        "journey":"Individual customer journey",
        "customer_orders":"Individual customer purchases",
        "risk":"Paid campaigns with low inventory",
    }
    name=st.selectbox("Read-only graph query",list(QUERIES),index=list(QUERIES).index("risk"),format_func=lambda key:query_labels.get(key,key))
    params={}
    if name in ("journey","customer_orders"): params={"customer":st.selectbox("Graph customer",[f"U{i:03}" for i in range(1,81)],key="graph_customer")}
    records=rows(db,name,params)
    st.caption(f"{len(records):,} matching records · Live embedded graph results")
    st.dataframe(records,hide_index=True,use_container_width=True,column_config={
        "campaign_id":"Campaign ID","campaign":"Campaign","channel":"Channel",
        "customer_id":"Customer ID","touchpoint_id":"Touchpoint ID","touchpoint":"Touchpoint",
        "conversion_id":"Conversion ID","order_id":"Order ID","occurred_at":"Touchpoint time",
        "converted_at":"Purchase time","product":"Product","promoted_product":"Promoted product",
        "stock":st.column_config.NumberColumn("Units in stock",format="%d"),
        "spend":st.column_config.NumberColumn("Campaign spend",format="dollar"),
        "revenue":st.column_config.NumberColumn("Revenue",format="dollar"),
        "cost":st.column_config.NumberColumn("Product cost",format="dollar"),
    })
    with st.expander("Technical audit — View Cypher query"):
        st.caption("Exact parameterized read-only query executed against Relate.")
        st.code(QUERIES[name],language="cypher")
        if params: st.json(params)
    st.subheader("Observed paths before first purchase")
    st.dataframe(path_insights(db),hide_index=True,use_container_width=True,column_config={"path":"Campaign path","purchasing_customers":"Purchasing customers"})
    st.caption("Counts among purchasing customers only; not path conversion rates or causal lift.")

def customer_view(db):
    st.subheader("Observed customer value")
    people,cohorts=customer_value(db)
    df=pd.DataFrame(cohorts)
    a,b,c=st.columns(3)
    a.metric("Observed customers",len(people))
    b.metric("Repeat purchasers",sum(p["orders"]>1 for p in people))
    c.metric("Observed revenue / customer",money(sum(p["revenue"] for p in people)/len(people)) if people else "N/A")
    chart_df=df.melt(id_vars="campaign_id",value_vars=["observed_revenue_per_customer","observed_gross_profit_per_customer"],var_name="metric",value_name="amount")
    chart_df["metric"]=chart_df["metric"].map({"observed_revenue_per_customer":"Revenue / customer","observed_gross_profit_per_customer":"Gross profit / customer"})
    chart=alt.Chart(chart_df).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("campaign_id:N",title="First observed campaign"),xOffset="metric:N",
        y=alt.Y("amount:Q",title="USD",axis=alt.Axis(format="$,.0f")),
        color=alt.Color("metric:N",title=None,scale=alt.Scale(domain=["Revenue / customer","Gross profit / customer"],range=["#20d8d0","#6689e8"])),
        tooltip=["campaign_id","metric",alt.Tooltip("amount:Q",format="$,.2f")]).properties(height=280)
    st.altair_chart(polish_chart(chart),use_container_width=True)
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.caption("Grouped by earliest recorded campaign touch before first purchase (or earliest touch for non-buyers). Includes non-buyers in customer averages. Not predicted lifetime value, verified acquisition source, or causal credit.")
    with st.expander("Customer-level evidence"): st.dataframe(people,hide_index=True,use_container_width=True)

def model_view(db):
    st.subheader("Attribution model sensitivity")
    df=pd.DataFrame(compare_models(db))
    st.dataframe(df.pivot(index="campaign",columns="model",values="attributed_revenue"),use_container_width=True)
    chart=alt.Chart(df).mark_bar().encode(x=alt.X("campaign:N",axis=alt.Axis(labelAngle=-20)),xOffset="model:N",y="attributed_revenue:Q",color=alt.Color("model:N",title=None,scale=alt.Scale(domain=["first_touch","last_touch","linear","position_based","time_decay"],range=["#6689e8","#20d8d0","#e5b86b","#a58be8","#91a6ba"])),tooltip=["campaign","model","attributed_revenue","profit_after_ads"]).properties(height=320)
    st.altair_chart(polish_chart(chart),use_container_width=True)
    st.caption("Five descriptive allocation models applied to the same graph-linked orders and touchpoints; none measures incremental lift.")

def budget_view(campaigns):
    st.subheader("Budget scenario simulator")
    st.info("Hypothetical fixed-budget sensitivity analysis, not a forecast. No advertising changes are made.")
    paid={c["campaign_id"]:c for c in campaigns if c["spend"]>0}
    if len(paid)<2: st.warning("At least two paid campaigns required."); return
    source=st.selectbox("Reduce spend from",list(paid),index=1,format_func=lambda k:paid[k]["campaign"])
    target=st.selectbox("Transfer spend to",[k for k in paid if k!=source],format_func=lambda k:paid[k]["campaign"])
    amount=st.number_input("Transfer amount (USD)",min_value=0.0,max_value=float(paid[source]["spend"]),value=0.0,step=25.0,key="transfer_"+source)
    factor=st.slider("Target marginal efficiency vs. historical gross profit / spend",0,100,50,5)/100
    data,warnings=scenario(campaigns,source,target,amount,factor)
    baseline=sum(r["baseline_profit"] for r in data); projected=sum(r["scenario_profit"] for r in data)
    a,b,c=st.columns(3)
    a.metric("Fixed total spend",money(sum(r["scenario_spend"] for r in data)))
    b.metric("Baseline attributed profit",money(baseline))
    c.metric("Scenario attributed profit",money(projected),delta=money(projected-baseline))
    for w in warnings: st.warning(w)
    frame=pd.DataFrame(data)
    long=frame.melt(id_vars="campaign",value_vars=["baseline_profit","scenario_profit"],var_name="case",value_name="profit")
    long["case"]=long["case"].map({"baseline_profit":"Baseline","scenario_profit":"Scenario"})
    chart=alt.Chart(long).mark_bar(cornerRadiusEnd=3).encode(
        y=alt.Y("campaign:N",title=None),yOffset="case:N",
        x=alt.X("profit:Q",title="Attributed profit after ads",axis=alt.Axis(format="$,.0f")),
        color=alt.Color("case:N",title=None,scale=alt.Scale(domain=["Baseline","Scenario"],range=["#91a6ba","#20d8d0"])),
        tooltip=["campaign","case",alt.Tooltip("profit:Q",format="$,.2f")]).properties(height=280)
    st.altair_chart(polish_chart(chart),use_container_width=True)
    st.dataframe(frame,hide_index=True,use_container_width=True)
    st.caption("Source gross profit loss assumes historical gross profit per dollar removed. Target gain assumes historical gross profit per dollar added multiplied by your selected factor. Organic is held constant. No stock-volume caps, cross-channel interactions, demand forecasts or causal effects modeled.")
    st.download_button("Download scenario CSV",frame.to_csv(index=False),"budget_scenario.csv","text/csv")
