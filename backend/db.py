import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    resource_group VARCHAR(255),
                    resources_scanned INTEGER DEFAULT 0,
                    issues_found INTEGER DEFAULT 0,
                    estimated_savings TEXT,
                    analysis_result JSONB,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()


def create_user(email: str, password_hash: str) -> dict:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
                (email, password_hash)
            )
            conn.commit()
            return dict(cur.fetchone())


def get_user_by_email(email: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None


def create_analysis(user_id: int, resource_group: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO analyses (user_id, resource_group, status) VALUES (%s, %s, 'running') RETURNING id",
                (user_id, resource_group)
            )
            conn.commit()
            return cur.fetchone()[0]


def update_analysis(analysis_id: int, resources_scanned: int, issues_found: int,
                    estimated_savings: str, result: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE analyses
                SET resources_scanned = %s,
                    issues_found = %s,
                    estimated_savings = %s,
                    analysis_result = %s,
                    status = 'complete'
                WHERE id = %s
            """, (resources_scanned, issues_found, estimated_savings, json.dumps(result), analysis_id))
            conn.commit()


def get_history(user_id: int) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, resource_group, resources_scanned, issues_found,
                       estimated_savings, status, created_at
                FROM analyses
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            return [dict(r) for r in cur.fetchall()]


def get_analysis_by_id(analysis_id: int, user_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM analyses WHERE id = %s AND user_id = %s",
                (analysis_id, user_id)
            )
            row = cur.fetchone()
            return dict(row) if row else None
