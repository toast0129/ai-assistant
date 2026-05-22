from backend.db.supabase_client import supabase

def is_duplicate(item_id: str, table: str, id_field: str) -> bool:
    res = supabase.table(table).select("id").eq(id_field, item_id).limit(1).execute()
    return len(res.data) > 0