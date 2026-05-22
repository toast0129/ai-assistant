from fastapi import APIRouter
from backend.db.supabase_client import supabase

router = APIRouter()

@router.get("/items")
def get_emails(importance_min: int = 3, limit: int = 20):
    """Return emails above importance threshold."""
    res = supabase.table("email_items") \
        .select("*") \
        .gte("importance", importance_min) \
        .order("received_at", desc=True) \
        .limit(limit) \
        .execute()
    return res.data

@router.post("/run")
def run_email_monitor():
    import traceback
    from fastapi.responses import JSONResponse
    try:
        from backend.scheduler.jobs import job_email_monitor
        job_email_monitor()
        return {"status": "triggered"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "detail": traceback.format_exc()})
