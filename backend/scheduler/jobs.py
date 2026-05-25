"""
Each job is a standalone function — callable from scheduler or manually via API.
"""
import httpx
from config.settings import settings
from config.prompts import GITHUB_DIGEST_SYSTEM, YOUTUBE_CURATOR_SYSTEM
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



def job_youtube_curator():
    """Search YouTube for AI + 3D gamedev videos (Chinese/English), filter by Claude."""
    import httpx
    queries = [
        # English
        "AI agent tutorial 2025",
        "RAG LLM tutorial 2025",
        "MCP Claude tools tutorial",
        "Unreal Engine 5 tutorial 2025",
        # Chinese
        "AI 教學 2025",
        "大型語言模型 LLM 教程",
        "Blender 3D 教學",
        "遊戲開發 Unity Unreal 教學",
    ]
    videos = []

    for q in queries:
        res = httpx.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part": "snippet", "q": q, "type": "video",
                    "maxResults": 10, "key": settings.youtube_api_key},
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

    # 讀取使用者偏好 URLs
    try:
        prefs_res = supabase.table("youtube_prefs").select("url").execute()
        pref_urls = [p["url"] for p in (prefs_res.data or [])]
    except Exception:
        pref_urls = []

    user_msg = "\n".join([f"{v['title']} ({v['channel']}): {v['description'][:100]}" for v in unique[:60]])
    if pref_urls:
        user_msg += "\n\n【使用者偏好參考】\n" + "\n".join(pref_urls[:15])

    results = call_claude(YOUTUBE_CURATOR_SYSTEM, user_msg, "youtube", max_tokens=8192)

    for item in results:
        vid_data = next((v for v in unique if v["title"] == item.get("title")), {})
        desc = vid_data.get("description", "") or item.get("title", "")

        vid_id = vid_data.get("video_id", "")
        if not vid_id:
            continue

        from datetime import datetime, timezone
        supabase.table("youtube_items").upsert({
            "video_id":    vid_id,
            "title":       item.get("title", ""),
            "channel":     item.get("channel", ""),
            "url":         vid_data.get("url", ""),
            "summary":     item.get("summary", ""),
            "value_score": item.get("value_score", 5),
            "fit_score":   item.get("fit_score", 5),
            "seen_at":     datetime.now(timezone.utc).isoformat(),
        }, on_conflict="video_id").execute()
