import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ai_analyzer import analyze_costs
from aws_scanner import get_aws_regions, scan_resources, verify_credentials
from db import (
    create_analysis,
    create_user,
    get_analysis_by_id,
    get_history,
    get_user_by_email,
    init_db,
    update_analysis,
)

load_dotenv()

app = FastAPI(title="AI Cloud Cost Detective")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

security = HTTPBearer()

# WebSocket connection manager
active_connections: dict[int, list[WebSocket]] = {}


@app.on_event("startup")
def startup():
    init_db()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict:
    return decode_token(credentials.credentials)


# ── Auth endpoints ────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
def signup(body: AuthRequest):
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    user = create_user(body.email, hashed)
    return {"token": create_token(user["id"], user["email"]), "email": user["email"]}


@app.post("/api/auth/login")
def login(body: AuthRequest):
    user = get_user_by_email(body.email)
    if not user or not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user["id"], user["email"]), "email": user["email"]}


# ── AWS endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/resource-groups")
def list_regions(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        verify_credentials()
    except Exception:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    try:
        return {"regions": get_aws_regions()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AnalyzeRequest(BaseModel):
    resource_group: str  # used as region name


@app.post("/api/analyze")
async def analyze(body: AnalyzeRequest, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = int(current_user["sub"])
    region = body.resource_group

    analysis_id = create_analysis(user_id, region)

    async def push(msg: str):
        for ws in active_connections.get(analysis_id, []):
            try:
                await ws.send_text(msg)
            except Exception:
                pass

    try:
        await push(f"Scanning resources in {region}...")
        resources = scan_resources(region)

        await push("Analyzing costs with Claude AI...")
        result = analyze_costs(resources)

        await push("Storing results...")
        update_analysis(
            analysis_id,
            resources_scanned=len(resources),
            issues_found=result.get("issues_found", len(result.get("issues", []))),
            estimated_savings=result.get("estimated_monthly_savings", "N/A"),
            result=result,
        )

        await push("Analysis complete")
        return {"analysis_id": analysis_id, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── History ───────────────────────────────────────────────────────────────────

@app.get("/api/history")
def history(current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = int(current_user["sub"])
    rows = get_history(user_id)
    for r in rows:
        if isinstance(r.get("created_at"), datetime):
            r["created_at"] = r["created_at"].isoformat()
    return rows


@app.get("/api/history/{analysis_id}")
def get_analysis(analysis_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = int(current_user["sub"])
    row = get_analysis_by_id(analysis_id, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if isinstance(row.get("created_at"), datetime):
        row["created_at"] = row["created_at"].isoformat()
    return row


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/progress/{analysis_id}")
async def ws_progress(websocket: WebSocket, analysis_id: int):
    await websocket.accept()
    active_connections.setdefault(analysis_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[analysis_id].remove(websocket)
