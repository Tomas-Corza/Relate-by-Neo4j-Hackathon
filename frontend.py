"""Executive workspace presentation; all data comes from existing analytics."""
from html import escape
import streamlit as st
import pandas as pd
from graph import rows
from ui_components import money, campaign_chart, profit_chart, analyst

ICONS = {
    "revenue": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 10h18m-6 5h3"/>',
    "profit": '<path d="M3 17l6-6 4 4 8-9m-6 0h6v6"/>',
    "spend": '<path d="M3 6h18M3 12h18M3 18h18"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>',
    "orders": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2M9 11h6m-6 4h6"/>',
    "ratio": '<path d="M4 20L20 4"/><circle cx="7" cy="7" r="3"/><circle cx="17" cy="17" r="3"/>',
    "graph": '<circle cx="5" cy="12" r="3"/><circle cx="19" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><path d="M8 11l8-5M8 13l8 5"/>',
}
def icon(name):
    return '<svg aria-hidden="true" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+ICONS[name]+'</svg>'

def metric(label, value, detail, symbol, tone="teal"):
    return f'<article class="nx-card nx-{tone}"><div class="nx-card-top"><span>{escape(label)}</span><span class="nx-icon">{icon(symbol)}</span></div><div class="nx-value">{escape(str(value))}</div><div class="nx-detail">{escape(detail)}</div></article>'

def executive_dashboard(db, totals, campaigns, model):
    revenue=float(totals["total_revenue"])
    attributed=float(totals["attributed_revenue"])
    spend=sum(c["spend"] for c in campaigns)
    profit=sum(c["profit_after_ads"] for c in campaigns)
    orders=rows(db,"orders")
    touches=rows(db,"touches")
    risks=rows(db,"risk")
    counts=pd.Series([o["customer_id"] for o in orders]).value_counts()
    cards=[
        metric("Total revenue",money(revenue),f'{totals["total_conversions"]} recorded conversions',"revenue"),
        metric("Attributed profit after ads",money(profit),"Gross profit less campaign spend","profit","rose" if profit<0 else "teal"),
        metric("Campaign spend",money(spend),f'{sum(c["spend"]>0 for c in campaigns)} funded campaigns',"spend","blue"),
        metric("Blended revenue / spend",f"{revenue/spend:.2f}x" if spend else "N/A","Includes organic revenue","ratio","blue"),
        metric("Attributed revenue",money(attributed),f'{totals["attributed_conversions"]} attributed conversions',"graph"),
        metric("Purchasing customers",len(counts),f'{int((counts>1).sum())} repeat purchasers',"orders","violet"),
    ]
    st.markdown(f'<section class="nx-overview"><div class="nx-eyebrow">PERFORMANCE / OVERVIEW</div><div class="nx-title-row"><h1>Executive dashboard</h1><span class="nx-status"><span></span> Synthetic workspace</span></div><p>Revenue, campaign economics and connected customer evidence in one workspace.</p><div class="nx-meta">Attribution model: {escape(model.replace("_"," ").title())} &nbsp; / &nbsp; Read-only analytics</div></section><div class="nx-grid">{"".join(cards)}</div>',unsafe_allow_html=True)
    st.caption("Blended revenue / spend includes organic revenue; not paid-channel ROAS. Profit excludes overhead, taxes, shipping and returns.")
    left,right=st.columns([1.7,1])
    with left:
        with st.container(border=True):
            st.subheader("Campaign performance")
            st.caption("Attributed revenue · Gross profit · Campaign spend")
            campaign_chart(campaigns)
    with right:
        with st.container(border=True):
            st.subheader("Intelligence priorities")
            items=[]
            for r in risks:
                items.append(f'<div class="nx-alert"><div class="nx-eyebrow nx-risk">INVENTORY RISK</div><strong>{escape(r["campaign"])} / {escape(r["product"])}</strong><p>{int(r["stock"])} units remaining · {escape(money(r["spend"]))} campaign spend</p><small>Review spend before replenishment.</small></div>')
            if not risks:
                items.append('<div class="nx-alert"><strong>No low-stock paid campaigns</strong></div>')
            paid=[c for c in campaigns if c["spend"]>0 and c["stock"]>=10]
            if paid:
                best=max(paid,key=lambda c:c["profit_after_ads"])
                items.append(f'<div class="nx-opportunity"><div class="nx-eyebrow">CONTROLLED TEST</div><strong>{escape(best["campaign"])}</strong><p>{escape(money(best["profit_after_ads"]))} attributed profit after ads</p><small>Evaluate marginal returns with a controlled test.</small></div>')
            st.markdown("".join(items),unsafe_allow_html=True)
            st.caption("Rule-based suggestions; no advertising changes executed.")
    left,right=st.columns([1.7,1])
    with left:
        with st.container(border=True):
            st.subheader("Profitability comparison")
            profit_chart(campaigns)
    with right:
        with st.container(border=True):
            st.subheader("Customer journey")
            st.markdown('<div class="nx-mini-grid">'+metric("Recorded touchpoints",len(touches),"Graph-linked marketing interactions","graph")+metric("Repeat purchasers",int((counts>1).sum()),"Customers with multiple orders","orders","violet")+'</div>',unsafe_allow_html=True)
            st.caption("Explore individual paths in Customers.")
    with st.container(border=True):
        st.subheader("AI analyst")
        analyst(db,model)

def apply_frontend_styles():
    st.markdown("""<style>
    [data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#080f19;}
    .block-container{max-width:1500px;padding-top:4.4rem;}
    .nexus-header{gap:.75rem;}
    .nexus-header img{width:40px;height:40px;}
    .nexus-header h1{font-size:1.35rem;margin:.1rem 0;}
    .nexus-header p{font-size:.75rem;}
    .nexus-header .nexus-kicker{font-size:.65rem;}
    .nexus-rule{background:#243448;margin:.25rem 0 .4rem;}
    [data-testid="stSidebar"]{background:#101b2b;}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.28rem;}
    [data-testid="stSidebar"] [data-testid="stButton"] button{min-height:2.4rem;}
    .nexus-nav-heading{margin:.85rem .75rem .35rem;}
    .nx-overview{padding:8px 0 5px;}
    .nx-eyebrow{color:#74d7d1;font-size:11px;letter-spacing:.13em;font-weight:700;}
    .nx-title-row{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;}
    .nx-title-row h1{font-size:clamp(1.8rem,3vw,2.45rem);font-weight:700;padding:0;margin:8px 0;line-height:1.15;}
    .nx-overview p{color:#a8b9cb;font-size:.92rem;margin:0 0 10px;}
    .nx-meta{color:#9cb0c4;font-size:.78rem;margin:4px 0;}
    .nx-status{border:1px solid #2b4650;border-radius:99px;padding:6px 11px;font-size:11px;color:#b4dedb;white-space:nowrap;}
    .nx-status span{display:inline-block;width:7px;height:7px;background:#20d8d0;border-radius:100%;margin-right:5px;}
    .nx-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;}
    .nx-card{background:linear-gradient(135deg,#16263a,#101d2d);border:1px solid #283c50;border-radius:13px;padding:17px 18px;min-width:0;}
    .nx-card-top{display:flex;justify-content:space-between;align-items:center;gap:8px;color:#c2d0df;font-size:.83rem;font-weight:500;}
    .nx-icon{display:grid;place-items:center;border-radius:10px;background:#183d45;color:#50e1d8;width:37px;height:37px;flex-shrink:0;}
    .nx-blue .nx-icon{color:#a8bcff;background:#24375a;}
    .nx-violet .nx-icon{color:#c8b1ff;background:#342b50;}
    .nx-rose .nx-icon{color:#ff9ca5;background:#462a37;}
    .nx-value{font-size:clamp(1.35rem,2.4vw,2.15rem);font-weight:700;letter-spacing:-.045em;line-height:1.3;margin:9px 0 5px;color:#f0f5fb;overflow-wrap:anywhere;}
    .nx-detail{font-size:.76rem;color:#9aafc4;line-height:1.4;}
    .nx-alert,.nx-opportunity{border:1px solid #3d4555;border-left:3px solid #f4bd67;border-radius:9px;padding:13px 14px;margin:10px 0;background:#1a2635;}
    .nx-opportunity{border-left-color:#20d8d0;background:#122b35;}
    .nx-risk{color:#f4bd67;}
    .nx-alert strong,.nx-opportunity strong{display:block;margin:5px 0;font-size:.97rem;}
    .nx-alert p,.nx-opportunity p{font-size:.84rem;margin:5px 0;color:#d6e1eb;}
    .nx-alert small,.nx-opportunity small{color:#a9b9ca;font-size:.76rem;}
    .nx-mini-grid{display:grid;gap:10px;}
    .nx-mini-grid .nx-card{padding:10px 13px;}
    [data-testid="stVerticalBlockBorderWrapper"]{background:#101b2b;border:1px solid #26394c;border-radius:14px;}
    @media(max-width:1050px){.nx-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
    @media(max-width:620px){.nx-grid{grid-template-columns:1fr;}.nx-title-row h1{font-size:1.7rem;}}
    </style>""",unsafe_allow_html=True)
