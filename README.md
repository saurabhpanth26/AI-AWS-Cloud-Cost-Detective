# AI Cloud Cost Detective

An AI-powered tool that investigates AWS cloud costs automatically. It scans resources in an AWS region, detects cost issues like over-provisioning and misconfigurations, and provides actionable suggestions with fixes.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite + TypeScript + Tailwind) |
| Backend | Python (FastAPI) |
| Auth | Custom JWT Auth (bcrypt + PyJWT) |
| Cloud Data | AWS SDK (boto3) |
| Cloud | AWS |
| AI Analysis | Google Gemini 2.0 Flash (free) |
| Database | PostgreSQL (Docker / AWS RDS) |
| Live Updates | FastAPI WebSocket |
| Containerisation | Docker + Docker Compose |

## Architecture

```
                              ┌──────────────┐
                              │     USER     │
                              └──────┬───────┘
                                     │
                                     ▼
                           ┌───────────────────┐
                           │  REACT FRONTEND   │
                           └────────┬──────────┘
                                    :
                                    : Login / Signup
                                    ▼
                           ┌───────────────────┐
                           │  PYTHON BACKEND   │
                           │    (FastAPI)      │
                           │                   │
                           │  · Custom JWT Auth│
                           └───┬───────┬───┬───┘
                               :       :   :
                ┌──────────────┘       :   └──────────────┐
                :                      :                  :
                ▼                      ▼                  ▼
         ┌─────────────┐     ┌──────────────┐    ┌──────────────┐
         │   AWS SDK   │     │   FASTAPI    │    │   GOOGLE     │
         │   (boto3)   │     │  WEBSOCKET   │    │  GEMINI API  │
         │             │     │  (Progress)  │    │              │
         │ EC2/RDS/S3  │     └──────┬───────┘    │ Cost Analysis│
         └──────┬──────┘            :            └──────┬───────┘
                :                   : Live updates      :
                ▼                   ▼                   :
         ┌─────────────┐   ┌───────────────┐            :
         │     AWS     │   │    REACT      │            :
         │  (Region /  │   │  (Progress    │            :
         │  Resources) │   │   Tracker)    │            :
         └─────────────┘   └───────────────┘            :
                                                        ▼
                                                 ┌──────────────┐
                                                 │  PostgreSQL  │
                                                 │  (Docker /   │
                                                 │   AWS RDS)   │
                                                 │ · users      │
                                                 │ · analyses   │
                                                 └──────┬───────┘
                                                        :
                                                        : Stored results
                                                        ▼
                                                 ┌───────────────┐
                                                 │    REACT      │
                                                 │ (Final Report │
                                                 │  + Suggestions│
                                                 │  + Fixes)     │
                                                 └───────────────┘
```

## Request Flow

```
①  User ─·─·─► React ─·─·─► FastAPI Auth ─·─·─► JWT (PostgreSQL)

②  User selects AWS Region ─·─·─► Python Backend

③  Python ─·─·─► boto3 ─·─·─► Fetches all resources in region

④  Python ─·─·─► FastAPI WebSocket ─·─·─► React (live progress)

⑤  Python ─·─·─► Google Gemini API ─·─·─► Cost analysis

⑥  Python ─·─·─► PostgreSQL ─·─·─► Stores analysis history

⑦  React ◄·─·─·─ Final report with suggestions & fixes
```

## What It Detects

- **Over-provisioned resources** — EC2 instances, RDS, or Lambda sized larger than needed
- **Unused resources** — Unattached EBS volumes, idle Elastic IPs, unused load balancers
- **Misconfigurations** — Wrong instance families, missing auto-scaling, no reserved instances
- **Storage & logging costs** — Excessive CloudWatch log retention, no S3 lifecycle policies

---

## Running on a Server (Docker — Recommended)

This is the recommended way to run the application in production or on any remote server (EC2, VPS, etc.).

### Prerequisites

- A Linux server (Ubuntu 22.04+ recommended) with **Docker** and **Docker Compose** installed
- AWS credentials with read access to the target account
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### 1. Install Docker (if not already installed)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone the repository

```bash
git clone https://github.com/your-org/ai-cloud-cost-detective.git
cd ai-cloud-cost-detective
```

### 3. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Fill in every value:

```env
GEMINI_API_KEY=AIzaSy...
JWT_SECRET=a_long_random_string_at_least_32_chars
POSTGRES_USER=costdetective
POSTGRES_PASSWORD=a_strong_password
POSTGRES_DB=costdetective

# AWS — leave blank if the server has an IAM role attached
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

> **Tip:** Generate a secure JWT secret with `openssl rand -hex 32`

### 4. Build and start all services

```bash
docker compose up -d --build
```

This starts three containers:

| Container  | What it runs                        | Port |
|------------|-------------------------------------|------|
| `db`       | PostgreSQL 16                       | internal only |
| `backend`  | FastAPI (Python)                    | `8000` |
| `frontend` | React app served by nginx           | `80` |

### 5. Verify everything is running

```bash
docker compose ps
docker compose logs -f
```

Open `http://<your-server-ip>` in a browser. You should see the login page.

### 6. Stopping and restarting

```bash
# Stop
docker compose down

# Restart (without rebuilding)
docker compose up -d

# Rebuild after a code change
docker compose up -d --build
```

### 7. View logs for a specific service

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

---

## Running Locally (Development)

Use this when developing — hot reload is enabled for both frontend and backend.

### Prerequisites

- Python 3.10+
- Node.js 18+
- A PostgreSQL instance (local or AWS RDS)
- AWS credentials (`aws configure` or environment variables)
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
uvicorn main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI available at http://localhost:5173
```

---

## How It Works

1. User signs up / logs in via custom JWT auth (credentials stored in PostgreSQL)
2. Selects an AWS region to analyze
3. Python backend fetches all resources using boto3
4. Live progress is streamed to the UI via FastAPI WebSocket
5. Resource data is sent to the Google Gemini API for cost analysis
6. Analysis results are stored in PostgreSQL
7. Final report with cost breakdown, suggestions, and fix commands is displayed

---

## Security Notes

- Never commit your `.env` file — it is listed in `.gitignore`
- Use a strong, unique `JWT_SECRET` in production
- Restrict the AWS IAM user/role to read-only permissions (e.g. `ReadOnlyAccess` policy)
- Place the server behind a reverse proxy (nginx / Caddy) with HTTPS for production use
