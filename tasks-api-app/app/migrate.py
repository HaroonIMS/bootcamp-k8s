import os

import psycopg

DATABASE_URL = os.environ["DATABASE_URL"]

# Every statement is safe to run twice. That is what makes a migration re-runnable.
with psycopg.connect(DATABASE_URL) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id    SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done  BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )
    # Version 2 of the schema: add a priority column if it is not there yet
    conn.execute(
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority INT NOT NULL DEFAULT 3"
    )

print("migrations applied")
