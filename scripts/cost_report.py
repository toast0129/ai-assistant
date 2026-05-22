"""Print a cost summary for today."""
from backend.db.supabase_client import supabase
from datetime import date

res = supabase.table("cost_log") \
    .select("module, cost_usd") \
    .gte("logged_at", str(date.today())) \
    .execute()

totals = {}
for row in res.data:
    totals[row["module"]] = totals.get(row["module"], 0) + float(row["cost_usd"])

print(f"\n=== Cost Report ({date.today()}) ===")
for module, cost in sorted(totals.items()):
    print(f"  {module:<12} ${cost:.4f}")
print(f"  {'TOTAL':<12} ${sum(totals.values()):.4f}")
