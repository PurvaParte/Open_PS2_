from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal
from app.core.config import settings
from app.models import (
    Session as SessionModel,
    Event,
    IntegritySignal,
    Concept,
    Prerequisite,
    StudentMastery,
    Question,
    Submission,
    VivaQuestion,
    VivaResponse,
    ReviewNote,
)
from app.schemas import EventCreate, EventOut
from app.events.recorder import record_event, SessionNotFoundError, InvalidEventError
from app.replay import get_session_events
from app.integrity import analyze_session
from app.database.seed import seed_initial_data
from app.routes import sessions_router, learning_router, assessment_router, trainer_router

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed default data on startup
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Adaptive Learning, Sandbox Coding Assessment & Evidence-Based Integrity Platform",
)

# Enable CORS for local development and demonstration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Core service metadata
@app.get("/")
def home():
    return {
        "message": "EvidentAI Backend Running",
        "database": "Connected",
        "version": settings.VERSION,
        "docs": "/docs",
    }

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(SessionModel.__table__.select().limit(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": str(e)}

# Include routers
app.include_router(sessions_router)
app.include_router(learning_router)
app.include_router(assessment_router)
app.include_router(trainer_router)
