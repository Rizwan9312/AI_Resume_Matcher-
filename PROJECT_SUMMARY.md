# ResumeIQ — AI Resume Matcher: Complete Project Summary

> **Last Updated:** 2026-05-03  
> **Purpose:** This document enables any AI model or developer to fully understand the current state of this project and continue work without prior context.

---

## 1. Project Overview

**ResumeIQ** is a full-stack, multi-tenant AI-powered resume analysis platform. Users upload a resume (PDF/DOCX) and a job description, and the system provides:

- **Multi-dimensional scoring** — BERT semantic similarity, TF-IDF cosine similarity, keyword overlap %, and LLM-as-judge scoring
- **Role-aware weighting** — auto-detects job role category (engineering, data science, design, etc.) and applies optimized score weights
- **Keyword gap analysis** — identifies matched and missing skills/keywords
- **AI bullet rewriter** — rewrites weak resume bullets into quantified, ATS-optimized statements
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
│   │   │   ├── rewrite_session.py # RewriteSession (AI rewrite history)
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
│   │   │   ├── rewriter.py       # AI bullet rewriting endpoint
│   │   │   ├── users.py          # User profile management
│   │   │   ├── tenants.py        # Tenant/workspace management
│   │   │   └── billing.py        # Billing stubs (Stripe-ready)
│   │   │
│   │   ├── services/             # Business logic layer
│   │   │   ├── auth_service.py   # Register, login, refresh, logout logic
│   │   │   ├── resume_service.py # Resume parsing orchestration
│   │   │   ├── match_service.py  # Match pipeline orchestration
│   │   │   ├── rewriter_service.py # Rewrite logic
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
│   │   │   ├── rewrite_tasks.py  # AI bullet rewriting pipeline
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
│   │   │   └── match/
│   │   │       ├── new/page.tsx  # New match analysis form
│   │   │       └── [id]/         # Match result detail view
│   │   ├── lib/
│   │   │   ├── api.ts            # Axios client with JWT interceptor + auto-refresh
│   │   │   └── utils.ts          # Utility functions (clsx/cn helper)
│   │   └── types/                # TypeScript type definitions
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
```

### Key Mixins
- **TimestampMixin** — adds `created_at` with `server_default=func.now()`
- **SoftDeleteMixin** — adds `deleted_at` for soft deletes (used by User, Resume, Tenant)

### Critical Note on Models
All models **MUST** be imported in `backend/app/models/__init__.py` for SQLAlchemy mapper resolution. Missing imports cause `NoReferencedColumnError` at startup. This was a recurring bug in past conversations.

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
| `POST` | `/rewriter/rewrite` | Yes | AI bullet rewriting |
| `GET` | `/users/me` | Yes | Get current user profile |
| `GET` | `/health` | No | Health check (DB + Redis status) |

### Authentication Flow
1. Client registers/logs in → receives `access_token` (JWT, 15min) + `refresh_token` (opaque hex, 30 days)
2. Access token sent as `Bearer` header via Axios interceptor
3. On 401 → auto-refresh via `/auth/refresh` → retry original request
4. Refresh tokens stored hashed (SHA-256) in DB with revocation support
5. Frontend stores tokens in-memory only (no localStorage for security)

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

### Role-Aware Weights (examples)
- **Software Engineering**: BERT 30%, TF-IDF 15%, Keywords 30%, LLM 25%
- **Data Science**: BERT 25%, TF-IDF 20%, Keywords 25%, LLM 30%
- **Design**: BERT 20%, TF-IDF 10%, Keywords 25%, LLM 45%

### LLM Integration
- **Provider**: OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`)
- **Default Model**: `qwen/qwen-2.5-coder-32b-instruct`
- **Output**: Structured JSON with `overall_fit`, `experience_match`, `skills_match`, `strengths`, `gaps`, `recommendation`
- **Retry Logic**: Re-prompts once on JSON parse failure with stricter instructions
- **Known Issue**: Some models (Qwen3 thinking models) don't support `json_object` response format properly

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

### Frontend Environment
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Set in next.config.js
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

# 4. (Optional) Start Celery worker for background processing
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### ⚠️ IMPORTANT: CWD Matters
The backend **MUST** be run from the `backend/` directory:
```bash
cd e:\new\AI_Resume_Matcher--main\backend
uvicorn app.main:app --reload --port 8000
```
Running from the project root causes `ModuleNotFoundError: No module named 'app'`.

### Database Auto-Creation
In development mode (`ENVIRONMENT=development`), tables are auto-created on startup via `Base.metadata.create_all`. No need to run Alembic migrations manually in dev.

---

## 9. Known Issues & Historical Bugs

### Resolved Issues (from past conversations)

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| **`ModuleNotFoundError: No module named 'app'`** | Running uvicorn from wrong directory (project root instead of `backend/`) | Must `cd backend` before running uvicorn |
| **SQLAlchemy mapper errors at startup** | Missing model imports in `models/__init__.py` | All models now imported in `__init__.py` |
| **`server_default` incompatibility** | Using Python enum values in `server_default` with asyncpg | Changed to string literals (e.g., `server_default="false"`) |
| **User registration failures** | Circular model dependencies + enum column issues | Fixed import order and enum definitions |
| **CORS blocking frontend requests** | `localhost:3000` not in allowed origins | Added `localhost:3000` and `127.0.0.1:3000` to CORS in dev mode |
| **Resume upload "failed to fetch"** | Backend not running / CORS misconfigured | Fixed CORS + ensured backend reachable |
| **LLM JSON parse failures** | Qwen3 thinking models wrapping output in markdown | Added regex to strip ```json fences; retry with stricter prompt |
| **Analysis stream race condition** | Frontend calling API before backend stream ready | Added proper state management + error boundaries |
| **OpenRouter rate limits** | Too many concurrent requests | Added model-switching fallback logic |

### Current Known Issues (as of 2026-05-03)

1. **Backend CWD sensitivity** — Must always run `uvicorn` from `backend/` directory
2. **Celery optional** — If Celery worker isn't running, match pipeline dispatch fails silently (match stays in `pending` status)
3. **spaCy model required** — `en_core_web_md` must be downloaded: `python -m spacy download en_core_web_md`
4. **BERT model download** — First run downloads `all-MiniLM-L6-v2` (~80MB), may timeout on slow connections
5. **Legacy files** — `backend/app.py`, `matcher.py`, `parser.py`, etc. are from pre-refactor and NOT used by the current enterprise architecture

---

## 10. Architecture Patterns

### Multi-Tenancy
- Every user belongs to a `Tenant` (workspace/organization)
- Registration auto-creates a personal tenant if none specified
- All data queries should be scoped by `tenant_id` for proper isolation

### Soft Deletes
- Users, Resumes, Tenants use `SoftDeleteMixin` with `deleted_at` column
- Queries filter by `deleted_at.is_(None)` to exclude soft-deleted records

### Service Layer
- API routes delegate to services (`services/`) for business logic
- Services use the async SQLAlchemy session pattern

### Async Everything
- Database: `asyncpg` + SQLAlchemy async sessions
- HTTP: `httpx.AsyncClient` for LLM API calls
- Celery bridge: Tasks create new event loops for async execution

### JWT Architecture
- Access tokens: Short-lived (15min), contain `sub` (user_id), `role`, `tenant_id`
- Refresh tokens: Long-lived (30 days), opaque hex, stored as SHA-256 hash in DB
- Token rotation: Old refresh token revoked on each refresh

---

## 11. Design System (Frontend)

- **Theme**: Dark mode only (HSL-based CSS custom properties)
- **Colors**: Deep navy background (`222 47% 5%`), blue primary (`217 91% 60%`), green accent (`160 60% 52%`)
- **Typography**: Inter (body) + JetBrains Mono (code)
- **Components**: Glassmorphism cards, gradient text, score ring animations
- **Score Colors**: Excellent (green `#3dd68c`), Good (yellow `#f5c842`), Moderate (orange `#f58442`), Low (red `#f54242`)

---

## 12. Conversation History Summary

| # | Date | Topic | Key Outcome |
|---|------|-------|-------------|
| 1 | Apr 25 | Initial setup & dependency installation | Fixed CORS, PDF parsing bug |
| 2 | Apr 25 | E2E pipeline testing | Validated full analysis pipeline |
| 3 | Apr 26 | Deployment finalization | Fixed cross-platform DB models, non-Docker setup |
| 4 | Apr 26 | Server debugging | Fixed race condition in analysis stream, Qwen3 model compat |
| 5 | Apr 27 | Stream fix | Fixed premature quit, fabrication check exceptions |
| 6 | Apr 29 | Startup commands | Documented manual launch sequence |
| 7 | Apr 29 | Port 8000 errors | Added LLM model-switching fallback, env standardization |
| 8 | Apr 30 | Fetch errors | Fixed API communication failures |
| 9 | May 02 | Enterprise refactor | Built full enterprise architecture (current codebase) |
| 10 | May 02-03 | Registration bugs | Fixed SQLAlchemy enum mapping, `server_default` issues |

### Evolution
The project evolved from a simple single-file Flask/Streamlit app to a **full enterprise FastAPI + Next.js architecture** with multi-tenancy, JWT auth, Celery workers, and a comprehensive ML scoring pipeline. The enterprise refactor (conversation #9) was the major architectural change.

---

## 13. Quick Reference for Continuing Work

### To fix something:
1. Check if backend is running from correct CWD (`backend/`)
2. Check Docker containers: `docker-compose up db redis -d`
3. Check `.env` files (backend has its own `.env`)
4. Check `models/__init__.py` if adding new models

### To add a new feature:
1. Add model in `backend/app/models/` → import in `models/__init__.py`
2. Add schema in `backend/app/schemas/`
3. Add service in `backend/app/services/`
4. Add API route in `backend/app/api/v1/` → register in `router.py`
5. Add frontend page in `frontend/src/app/`

### To debug:
- Backend logs: structured JSON via `structlog` with trace IDs
- Health check: `GET http://localhost:8000/health`
- API docs: `http://localhost:8000/docs` (Swagger UI, dev only)
- DB test: `python backend/check_db.py`
