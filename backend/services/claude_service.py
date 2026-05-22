import anthropic, json, re
from config.settings import settings
from backend.db.supabase_client import supabase

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

def call_claude(system: str, user: str, module: str, max_tokens: int = 1000):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    usage = response.usage
    cost = (usage.input_tokens * 3.0 + usage.output_tokens * 15.0) / 1_000_000

    supabase.table("cost_log").insert({
        "module": module,
        "tokens_in": usage.input_tokens,
        "tokens_out": usage.output_tokens,
        "cost_usd": float(cost),
    }).execute()

    text = response.content[0].text.strip()

    # 移除 markdown code block
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            text = match.group(1).strip()

    # 直接抓出 JSON array 或 object
    match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text)
    if match:
        text = match.group(1)

    return json.loads(text)