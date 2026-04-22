from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, exams, sessions, violations, examiner

app = FastAPI(
    title="Proctify API",
    version="2.0.0",
    description="AI-Powered Proctored Examination Platform",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── ROUTERS ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,       prefix="/api/auth",     tags=["Auth"])
app.include_router(exams.router,      prefix="/api/exams",    tags=["Exams"])
app.include_router(sessions.router,   prefix="/api/sessions", tags=["Sessions"])
app.include_router(violations.router, prefix="/api/sessions", tags=["Violations"])
app.include_router(examiner.router,   prefix="/api/examiner", tags=["Examiner"])

# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Proctify API", "version": "2.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
