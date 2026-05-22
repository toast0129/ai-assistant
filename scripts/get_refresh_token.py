"""
執行此腳本取得 Google Refresh Token
用法：python scripts/get_refresh_token.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

secret_file = Path(__file__).parent / "client_secret.json"

flow = InstalledAppFlow.from_client_secrets_file(
    str(secret_file),
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)

creds = flow.run_local_server(port=0)

print("\n=== 複製以下內容到 .env ===")
print(f"GOOGLE_CLIENT_ID={creds.client_id}")
print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
