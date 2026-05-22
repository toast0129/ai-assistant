import traceback
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.db.supabase_client import supabase

router = APIRouter()

@router.get("/digest")
def get_github_digest(limit: int = 10):
    """Return latest GitHub recommendations."""
    res = supabase.table("github_items") \
        .select("id,title,url,summary,stars,language,topics,score,seen_at") \
        .order("score", desc=True) \
        .order("seen_at", desc=True) \
        .limit(limit) \
        .execute()
    return res.data

@router.post("/run")
def run_github_digest():
    """Manually trigger GitHub digest job."""
    try:
        from backend.scheduler.jobs import job_github_digest
        job_github_digest()
        return {"status": "triggered"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "detail": traceback.format_exc()})
