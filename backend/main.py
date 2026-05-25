from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import github, youtube, feedback
from backend.scheduler.runner import start_scheduler
from config.settings import settings

app = FastAPI(title="AI Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(github.router,   prefix="/api/github",   tags=["github"])
app.include_router(youtube.router,  prefix="/api/youtube",  tags=["youtube"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.on_event("startup")
async def startup():
    if settings.enable_scheduler:
        start_scheduler()
    else:
        import logging
        logging.getLogger(__name__).info("Scheduler disabled (ENABLE_SCHEDULER=false)")

@app.get("/api/health")
def health():
    return {"status": "ok"}
