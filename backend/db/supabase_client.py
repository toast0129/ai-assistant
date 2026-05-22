from supabase import create_client, Client
from config.settings import settings
import psycopg2

# Supabase client (for simple CRUD)
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Direct psycopg2 (for pgvector queries)
def get_pg_conn():
    return psycopg2.connect(settings.database_url)
