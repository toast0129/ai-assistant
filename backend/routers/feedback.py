from fastapi import APIRouter
from pydantic import BaseModel
from backend.db.supabase_client import supabase
from typing import Literal

router = APIRouter()

class FeedbackIn(BaseModel):
    item_id: str
    item_type: Literal["github", "email", "youtube"]
    action: Literal["clicked", "dismissed", "saved"]

@router.post("/")
def submit_feedback(body: FeedbackIn):
    supabase.table("feedback").insert(body.model_dump()).execute()
    return {"status": "ok"}

@router.get("/stats")
def feedback_stats():
    """Return action counts per item_type for the last 30 days."""
    res = supabase.rpc("feedback_stats_30d").execute()
    return res.data
