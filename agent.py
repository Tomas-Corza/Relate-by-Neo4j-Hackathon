"""Read-only tool routing; optional LLM selects tools, never executes generated Cypher."""
import json
import os
import re
from graph import evidence, rows

def investigate(db, question, model="linear", api_key=None):
    context = evidence(db,model)
    customer = re.search(r"\bU\d{3}\b",question,re.I)
    if customer:
        uid=customer.group().upper()
        context["customer_journey"]=rows(db,"journey",{"customer":uid})
        context["customer_orders"]=rows(db,"customer_orders",{"customer":uid})
    key=api_key or os.getenv("OPENAI_API_KEY")
    if key:
        from openai import OpenAI
        client=OpenAI(api_key=key,timeout=25,max_retries=0)
        response=client.chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),messages=[
            {"role":"system","content":"You are a read-only marketing analyst. Answer solely from the supplied synthetic evidence. Cite campaign or order IDs, distinguish recommendations from facts, do not claim causality or execute changes. Say when evidence is insufficient."},
            {"role":"user","content":json.dumps({"question":question,"evidence":context})}])
        return response.choices[0].message.content,context
    if customer:
        answer=f"Customer {uid}: {len(context['customer_journey'])} recorded touchpoints and {len(context['customer_orders'])} orders. Review the evidence below."
    elif any(x in question.lower() for x in ("inventory","stock","risk")):
        answer="Inventory review: "+ "; ".join(f"{r['campaign_id']} promotes {r['product']} with {r['stock']} units; review spend of ${r['spend']:,}." for r in context["inventory_risks"])
    elif any(x in question.lower() for x in ("campaign","profit","roas","budget","spend")):
        ranked=sorted(context["campaigns"],key=lambda c:c["profit_after_ads"],reverse=True)
        answer="Descriptive profit after ads: "+ "; ".join(f"{c['campaign_id']} {c['campaign']}: ${c['profit_after_ads']:,.2f}" for c in ranked)+". Review negative contributors and inventory constraints before changing budgets."
    else:
        answer="Offline analyst supports campaign profitability, inventory risks and customer journeys (e.g. U001). Add an OpenAI key for broader natural-language analysis of this evidence."
    return answer,context
