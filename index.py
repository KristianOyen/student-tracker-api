from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    return sqlite3.connect("StudyTracker.db")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions(
                id INTEGER PRIMARY KEY, 
                subject TEXT,
                duration_minutes INTEGER,
                created_at TEXT
            )
        """)
        conn.commit()


@app.get("/sessions")
def get_sessions():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    
        query = "SELECT id, subject, duration_minutes, created_at FROM sessions"
        cursor.execute(query)

        return [dict(row) for row in cursor.fetchall()]


@app.post("/sessions")
async def create_sessions(request: Request):
    data = await request.json()
    subject = data["subject"]
    duration_minutes = data["duration_minutes"]
    created_at = datetime.now().strftime("%d.%m.%Y")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (subject, duration_minutes, created_at) VALUES (?, ?, ?)",
        (subject, duration_minutes, created_at),
    )
    conn.commit()
    conn.close()
    return {"created": True}


@app.delete("/sessions/{session_id}")
def delete_sessions(session_id: int):
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "DELETE FROM sessions WHERE id = ?"
        cursor.execute(query, (session_id,))

        conn.commit()
    
    return {"deleted": True}


