import psycopg2, pathlib
from config.settings import settings

sql = pathlib.Path("backend/db/schema.sql").read_text(encoding='utf-8')
with psycopg2.connect(settings.database_url) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
print("Schema applied.")