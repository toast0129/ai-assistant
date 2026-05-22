const BASE = "/api";

export async function fetchGithub(limit = 10) {
  const r = await fetch(`${BASE}/github/digest?limit=${limit}`);
  return r.json();
}

export async function fetchEmails(importanceMin = 3) {
  const r = await fetch(`${BASE}/email/items?importance_min=${importanceMin}`);
  return r.json();
}

export async function fetchYoutube(limit = 10) {
  const r = await fetch(`${BASE}/youtube/recommendations?limit=${limit}`);
  return r.json();
}

export async function submitFeedback(itemId, itemType, action) {
  await fetch(`${BASE}/feedback/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_id: itemId, item_type: itemType, action }),
  });
}

export async function triggerJob(module) {
  const r = await fetch(`${BASE}/${module}/run`, { method: "POST" });
  return r.json();
}
