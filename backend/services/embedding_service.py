import openai
from config.settings import settings

oa_client = openai.OpenAI(api_key=settings.openai_api_key)

def embed(texts: list[str]) -> list[list[float]]:
    """Batch embed texts using text-embedding-3-small."""
    if not texts:
        return []
    resp = oa_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [r.embedding for r in resp.data]
