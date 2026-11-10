import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Tasks API v2")


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    priority: int = Field(default=3, ge=1, le=5)


def row_to_task(row):
    return {"id": row[0], "title": row[1], "priority": row[2], "done": row[3]}


@app.get("/health")
def health():
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute(
            "SELECT id, title, priority, done FROM tasks ORDER BY id"
        ).fetchall()
    return [row_to_task(r) for r in rows]


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "INSERT INTO tasks (title, priority) VALUES (%s, %s) "
            "RETURNING id, title, priority, done",
            (task.title, task.priority),
        ).fetchone()
    return row_to_task(row)


@app.patch("/tasks/{task_id}")
def toggle_task(task_id: int):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "UPDATE tasks SET done = NOT done WHERE id = %s "
            "RETURNING id, title, priority, done",
            (task_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
    return row_to_task(row)
