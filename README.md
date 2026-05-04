# AI Resume Matcher — Enterprise Edition

An AI-powered resume intelligence platform that scores, rewrites, and optimizes resumes against job descriptions. Built for job seekers and enterprise HR teams.

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
┌───▼───┐  ┌────▼────┐   ┌───────▼──────────┐
│ Postgres│  │  Redis  │   │  Celery Workers  │
│   15   │  │    7    │   │ (ML Pipeline)    │
└────────┘  └─────────┘   └──────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic |
| Database | PostgreSQL 15 |
| Cache & Queue | Redis 7, Celery 5 |
| ML/AI | BERT (sentence-transformers), TF-IDF, spaCy, OpenRouter LLM |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Auth | JWT (HS256) with refresh token rotation |
| Storage | Local (dev) / S3 (production) |
| Containers | Docker + docker-compose |
| CI/CD | GitHub Actions |

## Quick Start

### Prerequisites
- Docker Desktop (for PostgreSQL + Redis)
- Python 3.11+
- Node.js 20+

### 1. Clone & Configure
```bash
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
```

### 2. Start Infrastructure
```bash
docker-compose up db redis -d
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements-dev.txt
python -m spacy download en_core_web_md
uvicorn app.main:app --reload --port 8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Open
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

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

## ML Pipeline

1. **PDF/DOCX Parsing** — pdfplumber with OCR fallback
2. **Keyword Extraction** — spaCy NLP + skill alias resolution
3. **BERT Semantic Score** — sentence-transformers cosine similarity
4. **TF-IDF Score** — sklearn lexical matching
5. **LLM Score** — OpenRouter API structured evaluation
6. **Role Detection** — 10 job family profiles with adaptive weights
7. **Final Score** — Role-weighted blend of all scores

## Environment Variables

See `.env.example` for the full list.

## License

MIT
