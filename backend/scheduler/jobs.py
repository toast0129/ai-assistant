"""
Each job is a standalone function — callable from scheduler or manually via API.
"""
import httpx
from config.settings import settings
from config.prompts import GITHUB_DIGEST_SYSTEM, EMAIL_MONITOR_SYSTEM, YOUTUBE_CURATOR_SYSTEM
from backend.services.claude_service import call_claude
from backend.services.dedup_service import is_duplicate
from backend.db.supabase_client import supabase, get_pg_conn


def job_github_digest():
    """Fetch trending GitHub repos, filter by Claude, dedup, store."""
    headers = {"Authorization": f"token {settings.github_token}"}
    topics = ["agent", "llm-agent", "skills", "project-management", "cowork"]
    repos = []

    for topic in topics:
        res = httpx.get(
            "https://api.github.com/search/repositories",
            params={"q": f"topic:{topic}", "sort": "stars", "per_page": 10},
            headers=headers,
        ).json()
        repos.extend(res.get("items", []))

    # Deduplicate repo_ids
    seen_ids = set()
    unique = [r for r in repos if r["full_name"] not in seen_ids and not seen_ids.add(r["full_name"])]

    # Claude filter
    user_msg = "\n".join([f"{r['full_name']}: {r.get('description','')}" for r in unique[:15]])
    results = call_claude(GITHUB_DIGEST_SYSTEM, user_msg, "github", max_tokens=8192)

    for item in results:
        repo_name = item.get("title", "")
        repo_data = next((r for r in unique if r["full_name"] == repo_name), {})
        desc = repo_data.get("description", "") or repo_name

        if is_duplicate(repo_name, "github_items", "repo_id"):
            continue

        supabase.table("github_items").upsert({
            "repo_id":  repo_name,
            "title":    repo_name,
            "url":      repo_data.get("html_url", ""),
            "summary":  item.get("summary", ""),
            "stars":    repo_data.get("stargazers_count", 0),
            "language": repo_data.get("language", ""),
            "topics":   repo_data.get("topics", []),
            "score":    item.get("score", 5),
        }, on_conflict="repo_id").execute()


def job_email_monitor():
    """Poll Gmail for unread emails, summarise important ones."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=settings.google_refresh_token,
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )
    service = build("gmail", "v1", credentials=creds)
    messages = service.users().messages().list(
        userId="me", q="is:unread", maxResults=10
    ).execute().get("messages", [])

    snippets = []
    meta = []
    for m in messages:
        detail = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        snippet = detail.get("snippet", "").replace('"', "'").replace("\n", " ")[:200]
        snippets.append(f"Subject: {headers.get('Subject','')} | From: {headers.get('From','')} | {snippet}")
        meta.append({"message_id": m["id"], "subject": headers.get("Subject",""), "sender": headers.get("From","")})

    if not snippets:
        return

    results = call_claude(EMAIL_MONITOR_SYSTEM, "\n\n".join(snippets), "email", max_tokens=8192)

    for i, item in enumerate(results):
        if i >= len(meta):
            break
        supabase.table("email_items").upsert({
            **meta[i],
            "importance":    item.get("importance", 1),
            "summary":       item.get("summary", ""),
            "action_needed": item.get("action_needed", False),
            "raw_snippet":   snippets[i][:500],
        }, on_conflict="message_id").execute()


def job_youtube_curator():
    """Search YouTube for AI + 3D gamedev videos, filter by Claude."""
    import httpx
    queries = ["AI agent 2025", "RAG LLM tutorial", "Blender game design", "Unreal Engine 5 2025"]
    videos = []

    for q in queries:
        res = httpx.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part": "snippet", "q": q, "type": "video",
                    "maxResults": 8, "key": settings.youtube_api_key},
        ).json()
        for item in res.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title":    item["snippet"]["title"],
                "channel":  item["snippet"]["channelTitle"],
                "url":      f"https://youtube.com/watch?v={item['id']['videoId']}",
                "description": item["snippet"]["description"],
            })

    seen_ids = set()
    unique = [v for v in videos if v["video_id"] not in seen_ids and not seen_ids.add(v["video_id"])]

    user_msg = "\n".join([f"{v['title']} ({v['channel']}): {v['description'][:100]}" for v in unique])
    results = call_claude(YOUTUBE_CURATOR_SYSTEM, user_msg, "youtube", max_tokens=4096)

    for item in results:
        vid_data = next((v for v in unique if v["title"] == item.get("title")), {})
        desc = vid_data.get("description", "") or item.get("title", "")

        if is_duplicate(vid_data.get("video_id", ""), "youtube_items", "video_id"):
            continue

        supabase.table("youtube_items").upsert({
            "video_id":   vid_data.get("video_id", ""),
            "title":      item.get("title", ""),
            "channel":    item.get("channel", ""),
            "url":        vid_data.get("url", ""),
            "summary":    item.get("summary", ""),
            "value_score": item.get("value_score", 5),
            "fit_score":   item.get("fit_score", 5),
        }, on_conflict="video_id").execute()
