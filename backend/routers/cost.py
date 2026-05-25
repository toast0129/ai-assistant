from fastapi import APIRouter
from backend.db.supabase_client import supabase

router = APIRouter()

@router.get("/summary")
def cost_summary():
    """Return token usage and cost grouped by module, today vs all-time."""
    res = supabase.table("cost_log") \
        .select("module,tokens_in,tokens_out,cost_usd,created_at") \
        .order("created_at", desc=True) \
        .limit(500) \
        .execute()

    rows = res.data or []

    from datetime import datetime, timezone, timedelta
    today = datetime.now(timezone.utc).date()

    modules = {}
    total_all = {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "runs": 0}
    total_today = {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "runs": 0}

    for r in rows:
        m = r["module"]
        if m not in modules:
            modules[m] = {
                "module": m,
                "all": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "runs": 0},
                "today": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "runs": 0},
                "recent": [],
            }

        is_today = r.get("created_at", "")[:10] == str(today)
        for scope in (["all"] + (["today"] if is_today else [])):
            d = modules[m][scope]
            d["tokens_in"]  += r.get("tokens_in", 0)
            d["tokens_out"] += r.get("tokens_out", 0)
            d["cost_usd"]   += r.get("cost_usd", 0.0)
            d["runs"]       += 1

        total_all["tokens_in"]  += r.get("tokens_in", 0)
        total_all["tokens_out"] += r.get("tokens_out", 0)
        total_all["cost_usd"]   += r.get("cost_usd", 0.0)
        total_all["runs"]       += 1
        if is_today:
            total_today["tokens_in"]  += r.get("tokens_in", 0)
            total_today["tokens_out"] += r.get("tokens_out", 0)
            total_today["cost_usd"]   += r.get("cost_usd", 0.0)
            total_today["runs"]       += 1

        if len(modules[m]["recent"]) < 10:
            modules[m]["recent"].append({
                "tokens_in":  r.get("tokens_in", 0),
                "tokens_out": r.get("tokens_out", 0),
                "cost_usd":   r.get("cost_usd", 0.0),
                "created_at": r.get("created_at", ""),
            })

    return {
        "modules": list(modules.values()),
        "total_all": total_all,
        "total_today": total_today,
    }
