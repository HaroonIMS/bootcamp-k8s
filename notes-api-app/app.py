import os
import socket
import psycopg2
import redis
from flask import Flask, jsonify, request

app = Flask(__name__)
cache = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379)

def db_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "notes"),
        user=os.getenv("DB_USER", "notes"),
        password=os.getenv("DB_PASSWORD", ""),
    )

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/visit")
def visit():
    return jsonify(visits=cache.incr("visits"))

@app.route("/notes", methods=["GET", "POST"])
def notes():
    conn = db_conn()
    cur = conn.cursor()
    if request.method == "POST":
        cur.execute("INSERT INTO notes (body) VALUES (%s)", (request.json["body"],))
        conn.commit()
    cur.execute("SELECT id, body FROM notes ORDER BY id")
    rows = [{"id": r[0], "body": r[1]} for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/")
def index():
    return jsonify(app="notes-api", version="1.3.0", container=socket.gethostname())
@app.route("/api/notes")
def api_notes():
    return jsonify([{"id": 1, "text": "Learn Docker"}])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
