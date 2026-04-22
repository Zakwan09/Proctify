from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # tests connection before use — detects dropped connections
    pool_size=5,              # reduced from 10 — Supabase free tier has a 15 connection limit
    max_overflow=10,
    pool_recycle=300,         # recycle connections every 5 minutes — prevents stale connections
    pool_timeout=30,          # wait up to 30s for a connection before erroring
    connect_args={
        "connect_timeout": 10,          # give up connecting after 10s
        "keepalives": 1,                # enable TCP keepalives
        "keepalives_idle": 30,          # send keepalive after 30s idle
        "keepalives_interval": 10,      # retry every 10s
        "keepalives_count": 5,          # give up after 5 failed keepalives
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()