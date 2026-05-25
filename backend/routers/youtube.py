from fastapi import APIRouter
from backend.db.supabase_client import supabase

router = APIRouter()

@router.get("/recommendations")
def get_youtube(limit: int = 20):
    res = supabase.table("youtube_items") \
        .select("id,title,channel,url,summary,value_score,fit_score,duration,seen_at") \
        .order("seen_at", desc=True) \
        .order("value_score", desc=True) \
        .limit(limit) \
        .execute()
    return res.data

@router.post("/run")
def run_youtube_curator():
    from backend.scheduler.jobs import job_youtube_curator
    job_youtube_curator()
    return {"status": "triggered"}
