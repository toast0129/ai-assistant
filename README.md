# AI Assistant

個人 AI 助理系統：GitHub 推薦 / Email 監控 / YouTube 推薦

## 快速開始

```bash
# 1. 安裝依賴
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 設定環境變數
cp config/.env.example .env
# 填入你的 API keys

# 3. 初始化資料庫（需先建立 Supabase 專案）
python scripts/init_db.py

# 4. 啟動後端（自動啟動排程）
uvicorn backend.main:app --port 8000 --reload

# 5. 開啟瀏覽器
# http://localhost:8000
```

## 手動觸發任務

```bash
curl -X POST http://localhost:8000/api/github/run
curl -X POST http://localhost:8000/api/email/run
curl -X POST http://localhost:8000/api/youtube/run
```

## 費用查看

```bash
python scripts/cost_report.py
```
