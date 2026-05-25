from fastapi import APIRouter
from backend.db.supabase_client import supabase

router = APIRouter()

@router.get("/recommendations")
def get_youtube(limit: int = 24):
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

# ===== 偏好 URL =====

@router.get("/prefs")
def get_prefs():
    res = supabase.table("youtube_prefs") \
        .select("id,url,added_at") \
        .order("added_at", desc=True) \
        .execute()
    return res.data

@router.post("/prefs")
def add_pref(body: dict):
    url = (body.get("url") or "").strip()
    if not url.startswith("http"):
        return {"error": "invalid URL"}
    supabase.table("youtube_prefs").upsert({"url": url}, on_conflict="url").execute()
    return {"status": "saved"}

@router.delete("/prefs/{pref_id}")
def delete_pref(pref_id: str):
    supabase.table("youtube_prefs").delete().eq("id", pref_id).execute()
    return {"status": "deleted"}
