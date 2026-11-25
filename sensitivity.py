"""Descriptive sensitivity across the five existing attribution models."""
from collections import defaultdict
from statistics import mean
from attribution import MODELS

def sensitivity(records):
    grouped=defaultdict(dict)
    for r in records:
        grouped[r["campaign_id"]][r["model"]]=r
    rankings={}
    for model in MODELS:
        values=[r[model]["attributed_revenue"] for r in grouped.values()]
        rankings[model]={cid:1+sum(v>r[model]["attributed_revenue"] for v in values) for cid,r in grouped.items()}
    output=[]
    for cid,by_model in sorted(grouped.items()):
        base=by_model["linear"]
        rev=[by_model[m]["attributed_revenue"] for m in MODELS]
        profits=[by_model[m]["profit_after_ads"] for m in MODELS]
        ranks=[rankings[m][cid] for m in MODELS]
        average=mean(rev)
        spread=max(rev)-min(rev)
        output.append(dict(campaign_id=cid,campaign=base["campaign"],channel=base["channel"],
            min_revenue=min(rev),max_revenue=max(rev),mean_revenue=round(average,2),
            revenue_range=round(spread,2),range_pct_of_mean=round(100*spread/average,2) if average else None,
            profitable_models=sum(p>0 for p in profits),loss_models=sum(p<0 for p in profits),
            break_even_models=sum(p==0 for p in profits),
            min_profit=min(profits),max_profit=max(profits),
            best_rank=min(ranks),worst_rank=max(ranks),
            first_minus_last=round(by_model["first_touch"]["attributed_revenue"]-by_model["last_touch"]["attributed_revenue"],2),
            model_deltas={m:round(100*(by_model[m]["attributed_revenue"]-base["attributed_revenue"])/base["attributed_revenue"],2) if base["attributed_revenue"] else None for m in MODELS}))
    return output
