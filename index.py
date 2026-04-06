from fastapi import FastAPI
import sqlite3


def get_db():
    conn = sqlite3.connect("StudyTracker.db")
    return conn


app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

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
            duration_minutes INTEGER
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions")
    rows = cursor.fetchall()
    conn.close()
    return rows


@app.post("/sessions")
def create_sessions(subject: str, duration: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (subject, duration_minutes) VALUES (?, ?)",
        (subject, duration),
    )
    conn.commit()
    conn.close()
    return {"created": True}


@app.delete("/sessions{id}")
def delete_sessions(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = ?", (id))
    conn.commit()
    conn.close()
    return {"deleted": True}
