# ResumeIQ — AI Resume Matcher (Enterprise Edition)

An enterprise-grade, multi-tenant AI-powered resume intelligence platform. Users upload resumes, paste job descriptions, and the system produces multi-dimensional match scores, AI-powered resume rewrites, and live job recommendations sourced from LinkedIn and Indeed.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Next.js 14 Frontend (TypeScript)            │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────┐
│              FastAPI Backend (Python 3.11)            │
│  Auth │ Resumes │ Jobs │ Matches │ Rewriter │ Admin  │
└───┬────────────┬─────────────────┬──────────────────┘
    │            │                 │
┌───▼────┐  ┌───▼─────┐   ┌──────▼───────────┐
│Postgres│  │  Redis  │   │  Celery Workers  │
│   15   │  │    7    │   │ (ML Pipeline)    │
└────────┘  └─────────┘   └──────────────────┘
```

## Core Features

| Feature | Description |
|---|---|
| **Multi-Signal Match Scoring** | BERT semantic similarity + TF-IDF + keyword overlap + LLM evaluation |
| **Role-Aware Weighting** | 10 industry profiles auto-detected from JD text (tech, finance, marketing, etc.) |
| **AI Resume Rewriting** | Bullet-level and full-resume rewrites optimized for ATS via OpenRouter LLM with immediate download |
| **Live Job Recommendations** | JSearch API fetches real-time postings from LinkedIn/Indeed, scored by TF-IDF relevance |
| **Multi-Tenant Architecture** | Row-level tenant isolation with Free/Pro/Enterprise plans |

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| **Framework** | FastAPI (async, Python 3.11+) |
| **Database** | PostgreSQL 15 via SQLAlchemy 2.0 (async, `asyncpg` driver) |
| **Migrations** | Alembic (auto-create in dev) |
| **Cache / Broker** | Redis 7 |
| **Task Queue** | Celery 5 (Redis broker/backend, `solo` pool on Windows) |
| **Auth** | JWT (HS256) — access + rotating refresh tokens, `python-jose` + `passlib[bcrypt]` |
| **ML / NLP** | `sentence-transformers` (all-MiniLM-L6-v2), `scikit-learn`, `spaCy` |
| **LLM Integration** | OpenRouter API → configurable model (default: `qwen/qwen-2.5-coder-32b-instruct`) |
| **Job Search API** | JSearch (RapidAPI) — LinkedIn, Indeed, Glassdoor aggregation |
| **File Parsing** | `pdfplumber`, `python-docx` |

### Frontend
| Layer | Technology |
|---|---|
| **Framework** | Next.js 14.2 (App Router) |
| **Language** | TypeScript 5.6 |
| **Styling** | Tailwind CSS 3.4 + custom **"Antigravity"** design system |
| **State / Data** | TanStack React Query 5 + Axios |
| **Design System** | Dark-mode-first glassmorphism, floating orbs, animated score rings, professional light-mode fallbacks |

### Infrastructure
| Component | Technology |
|---|---|
| **Containerization** | Docker Compose (5 services) |
| **Services** | `db` (Postgres 15), `redis`, `backend`, `worker` (Celery), `frontend` (Next.js) |
| **CI/CD** | GitHub Actions |

## Project Structure

```
AI_Resume_Matcher/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # FastAPI route handlers
│   │   │   ├── auth.py       # Register, login, refresh, logout, password reset
│   │   │   ├── resumes.py    # Upload, list, parse, download
│   │   │   ├── matches.py    # Create match, poll status, list
│   │   │   ├── rewriter.py   # Trigger rewrite pipeline, poll status
│   │   │   ├── jobs.py       # CRUD for job descriptions
│   │   │   ├── jobs_feed.py  # LinkedIn/Indeed job recommendations
│   │   │   └── router.py     # Aggregates sub-routers
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic layer
│   │   ├── ml/               # ML pipeline (BERT, TF-IDF, LLM Scorer, Role Detector)
│   │   ├── workers/          # Celery tasks (match, rewrite, linkedin)
│   │   ├── utils/            # Shared utilities (security, cache, logger, file_utils)
│   │   └── main.py           # App factory + lifespan events
│   ├── migrations/           # Alembic scripts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing page
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── dashboard/          # Dashboard (stats, recent matches, live job feed)
│   │   │   ├── match/              # Match analysis workflow & detail view
│   │   │   ├── rewrite/            # AI resume rewriter workflow
│   │   │   └── (auth)/             # Login, register, password flows
│   │   ├── components/             # Reusable UI components
│   │   ├── lib/                    # api.ts (Axios + interceptor), utils.ts
│   │   └── types/                  # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── docker-compose.yml
├── .env / .env.example
└── README.md
```

## ML Pipeline

### A. Match Scoring (Celery: `match.run_pipeline`)
1. Extract plain text + sections from PDF/DOCX
2. Extract hard/soft skills via spaCy NER + regex
3. Compute BERT semantic similarity & TF-IDF cosine similarity
4. Calculate keyword overlap (matched / total JD keywords)
5. OpenRouter LLM evaluates structured JSON verdict (strengths, gaps, fit)
6. Auto-detect job role and apply weighted formula for final score
7. Save to DB → triggers `fetch_linkedin_jobs` in the background

### B. AI Resume Rewrite (Celery: `rewrite.run_full_pipeline`)
1. User receives a low score → clicks "Auto-Rewrite"
2. Background task passes entire resume and JD to OpenRouter LLM
3. LLM returns a fully rewritten, ATS-optimized resume with impact metrics
4. User can immediately download the `.txt` version

### C. Live Job Recommendations (Celery: `tasks.fetch_linkedin_jobs`)
1. Triggered automatically on dashboard mount or match completion
2. Extracts job search queries from resume
3. Fetches real-time LinkedIn/Indeed jobs via JSearch API
4. TF-IDF scores jobs against the user's resume
5. Saves top 20 matches to DB — frontend polls `/api/v1/jobs-feed/`

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register user |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/refresh | Refresh tokens |
| POST | /api/v1/resumes | Upload resume |
| GET | /api/v1/resumes | List resumes |
| POST | /api/v1/jobs | Save job description |
| POST | /api/v1/matches | Start match analysis |
| GET | /api/v1/matches/{id} | Get match result |
| POST | /api/v1/rewriter | Start bullet rewrite |
| GET | /api/v1/rewriter/{id} | Get rewrite result |
| GET | /api/v1/jobs-feed/ | Get job recommendations |
| POST | /api/v1/jobs-feed/trigger | Trigger job fetch |
| PATCH | /api/v1/jobs-feed/{id}/dismiss | Dismiss a job |

## Quick Start

### Prerequisites
- Docker Desktop (for PostgreSQL + Redis)
- Python 3.11+
- Node.js 20+

### 1. Clone & Configure
```bash
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY and JSEARCH_API_KEY
```

### 2. Start Infrastructure
```bash
docker-compose up db redis -d
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_md
uvicorn app.main:app --reload --port 8000
```

### 4. Start Celery Worker (Windows)
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Open
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Environment Variables

See `.env.example` for the full list. Key variables include:

- `OPENROUTER_API_KEY` — LLM provider key
- `JSEARCH_API_KEY` — RapidAPI key for LinkedIn/Indeed job feed
- `DATABASE_URL` — PostgreSQL async connection string
- `REDIS_URL` — Redis connection string
- `JWT_SECRET_KEY` — Secret for signing JWT tokens

## Recent Fixes & Improvements

- **Job Feed Visibility** — `/api/v1/jobs-feed/` now falls back to `resume_id` instead of strictly requiring `match_result_id`, ensuring jobs correctly display on match result pages
- **Celery Event Loop Isolation** — Rewrote background tasks to use short-lived isolated engines (`create_async_engine`) and isolated event loops per task, fixing SQLAlchemy `TimeoutError` and `Event loop is closed` crashes
- **Antigravity Redesign** — Full frontend overhaul into a premium dark-mode enterprise aesthetic with animated score rings and glowing floating orbs
- **React Query Fix** — Fixed missing `QueryClientProvider` in layout that broke `JobRecommendations`
- **Docker Redis Connectivity** — Resolved local Docker binding issues preventing backend–Redis communication
- **API Security** — Removed hardcoded keys, centralized configuration via `.env` validation

## License

MIT
