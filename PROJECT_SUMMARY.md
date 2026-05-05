# ResumeIQ — AI Resume Matcher: Complete Project Summary

> **Last Updated:** 2026-05-05  
> **Purpose:** This document enables any AI model or developer to fully understand the current state of this project and continue work without prior context.

---

## 1. Project Overview

**ResumeIQ** is a full-stack, multi-tenant AI-powered resume analysis platform. Users upload a resume (PDF/DOCX) and a job description, and the system provides:

- **Multi-dimensional scoring** — BERT semantic similarity, TF-IDF cosine similarity, keyword overlap %, and LLM-as-judge scoring
- **Role-aware weighting** — auto-detects job role category (engineering, data science, design, etc.) and applies optimized score weights
- **Keyword gap analysis** — identifies matched and missing skills/keywords
- **Auto-Rewrite Resume Feature** — A complete AI pipeline that takes a low-scoring resume and entirely rewrites it to match the job description, providing new ATS keywords, section-by-section feedback, and an instant download of the new optimized resume.
- **Feedback generation** — actionable plain-text feedback based on score tiers

The app is branded as **"ResumeIQ"** in the UI.

---

## 2. Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI (Python 3.13) |
| **Server** | Uvicorn with hot-reload |
| **Database** | PostgreSQL 15 (via `asyncpg` + SQLAlchemy 2.x async) |
| **Cache/Queue** | Redis 7 (used for caching + Celery broker) |
| **Task Queue** | Celery (Redis broker/backend) |
| **Auth** | JWT (HS256) via `python-jose` + bcrypt password hashing via `passlib` |
| **File Parsing** | `pdfplumber` (PDF), `python-docx` (DOCX) |
| **ML/NLP** | `sentence-transformers` (BERT), `scikit-learn` (TF-IDF), `spacy` (NER/keywords) |
| **LLM** | OpenRouter API (`qwen/qwen-2.5-coder-32b-instruct` default model) |
| **HTTP Client** | `httpx` (async) |
| **Logging** | `structlog` (structured JSON logging with trace IDs) |
| **Rate Limiting** | `slowapi` |
| **Config** | `pydantic-settings` (env var validation from `.env`) |

### Frontend
| Layer | Technology |
|-------|-----------|
| **Framework** | Next.js 14.2.15 (App Router, TypeScript) |
| **UI** | React 18, TailwindCSS 3.4, `lucide-react` icons |
| **HTTP** | Axios with JWT interceptor + auto-refresh |
| **State** | `@tanstack/react-query` v5 |
| **Design** | Dark mode, glassmorphism, Inter + JetBrains Mono fonts |

### Infrastructure
| Component | Details |
|-----------|---------|
| **Docker Compose** | Orchestrates `db` (Postgres), `redis`, `backend`, `worker`, `frontend` |
| **Dev Mode** | Run services individually outside Docker (current approach) |
| **Migrations** | Alembic (configured but dev mode auto-creates tables via `Base.metadata.create_all`) |

---

## 3. Project Structure

```
AI_Resume_Matcher--main/
├── .env                          # Root env (OpenRouter API key for docker-compose)
├── docker-compose.yml            # Full stack orchestration
├── requirements.txt              # Root-level deps reference
│
├── backend/
│   ├── .env                      # Backend env (all config: DB, Redis, JWT, AI, etc.)
│   ├── requirements.txt          # Python dependencies
│   ├── alembic.ini               # DB migration config
│   ├── migrations/               # Alembic migration scripts
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app factory + lifespan (startup/shutdown)
│   │   ├── config.py             # Pydantic Settings (all env vars)
│   │   ├── database.py           # SQLAlchemy async engine, Base, session factory, mixins
│   │   ├── middleware.py         # CORS, request logging, rate limiting
│   │   ├── dependencies.py       # Auth dependencies (get_current_user, require_role)
│   │   │
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── __init__.py       # Imports ALL models (critical for mapper resolution)
│   │   │   ├── tenant.py         # Tenant (multi-tenant org, has PlanType enum)
│   │   │   ├── user.py           # User + RefreshToken (has UserRole enum)
│   │   │   ├── resume.py         # Resume (uploaded file + parsed text)
│   │   │   ├── job_description.py # JobDescription (raw JD text)
│   │   │   ├── match_result.py   # MatchResult (all scores, keywords, LLM verdict)
│   │   │   ├── rewrite_session.py # RewriteSession (AI rewrite history/results)
│   │   │   └── subscription.py   # Subscription + UsageEvent (billing stubs)
│   │   │
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── auth.py           # Register/Login/Token schemas
│   │   │   ├── resume.py         # Resume CRUD schemas
│   │   │   ├── job.py            # Job description schemas
│   │   │   ├── match.py          # Match create/response schemas
│   │   │   ├── rewriter.py       # Rewrite request/response schemas
│   │   │   └── user.py           # User profile schemas
│   │   │
│   │   ├── api/v1/               # API route handlers (all under /api/v1)
│   │   │   ├── router.py         # Aggregates all sub-routers
│   │   │   ├── auth.py           # POST /register, /login, /refresh, /logout
│   │   │   ├── resumes.py        # CRUD: upload, list, get, delete resumes
│   │   │   ├── jobs.py           # CRUD: create, list, get job descriptions
│   │   │   ├── matches.py        # Create match, get result, list (with polling)
│   │   │   ├── rewriter.py       # Auto-Rewrite endpoints (POST /rewrites, GET /rewrites/{id})
│   │   │   ├── users.py          # User profile management
│   │   │   ├── tenants.py        # Tenant/workspace management
│   │   │   └── billing.py        # Billing stubs (Stripe-ready)
│   │   │
│   │   ├── services/             # Business logic layer
│   │   │   ├── auth_service.py   # Register, login, refresh, logout logic
│   │   │   ├── resume_service.py # Resume parsing orchestration
│   │   │   ├── match_service.py  # Match pipeline orchestration
│   │   │   ├── rewriter_service.py # Legacy rewrite logic
│   │   │   ├── billing_service.py  # Billing stubs
│   │   │   └── notification_service.py # Notification stubs
│   │   │
│   │   ├── ml/                   # ML/AI pipeline modules
│   │   │   ├── bert_encoder.py   # BERT semantic similarity (sentence-transformers)
│   │   │   ├── tfidf_scorer.py   # TF-IDF cosine similarity (scikit-learn)
│   │   │   ├── keyword_extractor.py # Hard/soft skill matching + spaCy NER
│   │   │   ├── llm_scorer.py     # OpenRouter LLM-as-judge scoring
│   │   │   ├── role_detector.py  # Job role detection + dynamic weight calculation
│   │   │   ├── section_parser.py # Resume section parsing (experience, education, etc.)
│   │   │   └── skill_graph.py    # Skill alias resolution + implied skill expansion
│   │   │
│   │   ├── workers/              # Celery background tasks
│   │   │   ├── celery_app.py     # Celery configuration
│   │   │   ├── match_tasks.py    # Full match scoring pipeline (async)
│   │   │   ├── rewrite_tasks.py  # AI full-resume & bullet rewriting pipeline
│   │   │   └── notification_tasks.py # Email notification stubs
│   │   │
│   │   └── utils/                # Shared utilities
│   │       ├── cache.py          # Redis client + health check
│   │       ├── file_utils.py     # File upload/download, validation, S3/local storage
│   │       ├── logger.py         # Structlog setup + trace ID generation
│   │       └── security.py       # JWT creation/decode, bcrypt hashing
│   │
│   ├── app.py                    # Legacy standalone app (pre-refactor)
│   ├── matcher.py                # Legacy matching logic
│   ├── parser.py                 # Legacy PDF parser
│   ├── keywords.py               # Legacy keyword lists
│   ├── rewriter.py               # Legacy rewriter
│   ├── role_score.py             # Legacy role scoring
│   ├── chatbot.py                # Legacy chatbot
│   ├── check_db.py               # DB connection test script
│   ├── reset_db.py               # DB reset utility
│   └── test_register.py          # Registration test script
│
├── frontend/
│   ├── package.json              # Dependencies (Next.js 14, React 18, Axios, etc.)
│   ├── next.config.js            # Standalone output, API URL env
│   ├── tailwind.config.ts        # Dark theme with custom design tokens
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx        # Root layout (dark mode, Inter font, metadata)
│   │   │   ├── globals.css       # Design system (HSL tokens, glassmorphism, animations)
│   │   │   ├── page.tsx          # Landing page (hero + feature cards)
│   │   │   ├── (auth)/
│   │   │   │   ├── login/        # Login page
│   │   │   │   └── register/     # Registration page
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx      # Main dashboard
│   │   │   │   ├── resumes/      # Resume management
│   │   │   │   └── matches/      # Match history
│   │   │   ├── match/
│   │   │   │   ├── new/page.tsx  # New match analysis form
│   │   │   │   └── [id]/         # Match result detail view (contains Auto-Rewrite trigger)
│   │   │   └── rewrite/
│   │   │       └── [match_id]/   # Dedicated page for the AI resume rewriting process & download
│   │   ├── lib/
│   │   │   ├── api.ts            # Axios client with JWT interceptor + auto-refresh
│   │   │   └── utils.ts          # Utility functions (clsx/cn helper)
│   │   └── types/                # TypeScript type definitions (contains new RewriteSession type)
│   └── Dockerfile
│
└── data/                         # Data directory (sample files, etc.)
```

---

## 4. Data Models & Relationships

```mermaid
erDiagram
    Tenant ||--o{ User : "has many"
    Tenant ||--o| Subscription : "has one"
    User ||--o{ RefreshToken : "has many"
    User ||--o{ Resume : "has many"
    User ||--o{ JobDescription : "has many"
    User ||--o{ MatchResult : "has many"
    Resume ||--o{ MatchResult : "has many"
    JobDescription ||--o{ MatchResult : "has many"
    MatchResult ||--o{ RewriteSession : "has many"

    Tenant {
        uuid id PK
        string name
        string slug UK
        enum plan "free|pro|enterprise"
        string api_key_hash
    }

    User {
        uuid id PK
        uuid tenant_id FK
        string email UK
        string password_hash
        enum role "job_seeker|recruiter|admin"
        string full_name
        bool is_verified
        string google_id
        datetime last_login_at
    }

    Resume {
        uuid id PK
        uuid user_id FK
        uuid tenant_id FK
        string filename
        string s3_key
        int file_size_bytes
        string mime_type
        text parsed_text
        jsonb parsed_sections
        enum parse_status "pending|done|failed"
    }

    MatchResult {
        uuid id PK
        uuid user_id FK
        uuid resume_id FK
        uuid job_id FK
        enum status "pending|processing|complete|failed"
        decimal bert_score
        decimal tfidf_score
        decimal keyword_score
        decimal llm_score
        decimal final_score
        string role_detected
        jsonb weights_used
        jsonb score_breakdown
        jsonb matched_keywords
        jsonb missing_keywords
        jsonb llm_verdict
        text feedback_text
    }

    RewriteSession {
        uuid id PK
        uuid user_id FK
        uuid match_id FK
        uuid resume_id FK
        text jd_text
        enum status "pending|complete|failed"
        jsonb rewrites
    }
```

### Critical Note on Models
All models **MUST** be imported in `backend/app/models/__init__.py` for SQLAlchemy mapper resolution. Missing imports cause `NoReferencedColumnError` at startup.

---

## 5. API Endpoints

All routes are prefixed with `/api/v1`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | No | Register new user (auto-creates tenant) |
| `POST` | `/auth/login` | No | Login with email/password |
| `POST` | `/auth/refresh` | No | Rotate refresh token |
| `POST` | `/auth/logout` | Yes | Revoke refresh token |
| `POST` | `/resumes` | Yes | Upload resume file (PDF/DOCX, max 10MB) |
| `GET` | `/resumes` | Yes | List user's resumes |
| `GET` | `/resumes/{id}` | Yes | Get specific resume |
| `DELETE` | `/resumes/{id}` | Yes | Soft-delete resume |
| `POST` | `/jobs` | Yes | Create job description |
| `GET` | `/jobs` | Yes | List job descriptions |
| `GET` | `/jobs/{id}` | Yes | Get specific JD |
| `POST` | `/matches` | Yes | Start match analysis (returns 202 + match_id) |
| `GET` | `/matches/{id}` | Yes | Get match result (used for polling) |
| `GET` | `/matches` | Yes | List matches (paginated, filterable by status) |
| `POST` | `/rewrites` | Yes | Start AI Full Resume Rewrite (needs `match_id`) |
| `GET` | `/rewrites/{id}`| Yes | Poll rewrite session status/results |
| `GET` | `/users/me` | Yes | Get current user profile |
| `GET` | `/health` | No | Health check (DB + Redis status) |

---

## 6. ML Scoring Pipeline

The match pipeline runs in a Celery worker (`workers/match_tasks.py`) and executes these steps:

```
1. Parse Resume  →  Extract text from PDF/DOCX, segment into sections
2. Extract Keywords  →  Hard skills + soft skills + spaCy NER entities
3. BERT Score  →  Sentence-transformer cosine similarity (0-100)
4. TF-IDF Score  →  Scikit-learn TfidfVectorizer cosine similarity (0-100)
5. Keyword Score  →  |matched ∩ required| / |required| × 100
6. LLM Score  →  OpenRouter API structured evaluation (0-100)
7. Role Detection  →  Classify job type + apply role-specific weights
8. Final Score  →  Weighted average based on detected role
9. Feedback  →  Tier-based text + missing skills summary
```

---

## 7. Configuration

### Backend `.env` (all variables)
```env
# App
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development          # development|staging|production
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256

# AI
OPENROUTER_API_KEY=sk-or-v1-...  # Required for LLM scoring
LLM_MODEL=qwen/qwen-2.5-coder-32b-instruct

# Storage
STORAGE_BACKEND=local            # "local" or "s3"
LOCAL_UPLOAD_DIR=uploads

# Frontend
FRONTEND_URL=http://localhost:3000
```

---

## 8. How to Run Locally (Development)

### Prerequisites
- Python 3.13+
- Node.js 18+
- Docker (for PostgreSQL + Redis)

### Step-by-step

```bash
# 1. Start infrastructure (PostgreSQL + Redis via Docker)
cd e:\new\AI_Resume_Matcher--main
docker-compose up db redis -d

# 2. Start backend (from the backend directory)
cd backend
pip install -r requirements.txt       # One-time
uvicorn app.main:app --reload --port 8000

# 3. Start frontend (from the frontend directory)
cd frontend
npm install                            # One-time
npm run dev                            # Starts on http://localhost:3000

# 4. Start Celery worker for background processing
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### ⚠️ IMPORTANT: CWD Matters
The backend **MUST** be run from the `backend/` directory:
```bash
cd e:\new\AI_Resume_Matcher--main\backend
uvicorn app.main:app --reload --port 8000
```

---

## 9. Known Issues & Historical Bugs

### Resolved Issues
| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| **`ModuleNotFoundError`** | Running uvicorn from wrong directory | Must `cd backend` before running uvicorn |
| **SQLAlchemy mapper errors** | Missing model imports | All models now imported in `__init__.py` |
| **`server_default` errors** | Python enum values in asyncpg | Changed to string literals (`"false"`) |
| **Large Git Commits** | Next.js binaries not in `.gitignore` | Ignored `node_modules` & `.next`, cleared git cache |
| **Celery Tasks Not Found** | Running stale Celery worker | Required `CTRL+C` & restart of Celery worker terminal |
| **Router ImportError** | Celery tasks placed in `api/v1/rewriter.py`| Moved logic to `workers/`, exposed correct FastAPI endpoints |

---

## 10. Conversation History Summary

| # | Date | Topic | Key Outcome |
|---|------|-------|-------------|
| 1 | Apr 25 | Initial setup & dependency installation | Fixed CORS, PDF parsing bug |
| 2 | Apr 25 | E2E pipeline testing | Validated full analysis pipeline |
| 3 | Apr 26 | Deployment finalization | Fixed cross-platform DB models, non-Docker setup |
| 4 | Apr 26 | Server debugging | Fixed race condition in analysis stream |
| 5 | Apr 27 | Stream fix | Fixed premature quit, fabrication check exceptions |
| 6 | Apr 29 | Startup commands | Documented manual launch sequence |
| 7 | Apr 29 | Port 8000 errors | Added LLM model-switching fallback |
| 8 | Apr 30 | Fetch errors | Fixed API communication failures |
| 9 | May 02 | Enterprise refactor | Built full enterprise architecture |
| 10 | May 02-03 | Registration bugs | Fixed SQLAlchemy enum mapping issues |
| 11 | May 04 | Git Push & Secrets check | Verified no hardcoded API keys, updated `.gitignore` for Next.js, pushed to GitHub successfully |
| 12 | May 04-05 | **Auto-Rewrite Feature** | Built a complete UI/API pipeline for automatically rewriting a low-scoring resume via OpenRouter AI. Included a "Download .txt" feature, new Celery Tasks, and updated Database schemas. |

### Evolution
The project evolved from a simple single-file Flask/Streamlit app to a **full enterprise FastAPI + Next.js architecture** with multi-tenancy, JWT auth, Celery workers, a comprehensive ML scoring pipeline, and fully automated AI-driven resume generation.
