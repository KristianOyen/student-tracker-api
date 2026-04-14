from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect("StudyTracker.db")
    return conn


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions(
            id INTEGER PRIMARY KEY, 
            subject TEXT,
            duration_minutes INTEGER,
            created_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


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


@app.delete("/sessions/{id}")
def delete_sessions(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"deleted": True}
