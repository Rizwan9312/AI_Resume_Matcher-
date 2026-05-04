# AI Resume Matcher — Enterprise Edition
### Master Build Specification for Antigravity (SKILL.md)

**One-line description:** An AI-powered resume intelligence platform that scores, rewrites, and optimizes resumes against job descriptions — built for both individual job seekers and enterprise HR teams.

**Problem solved:** Job seekers waste hours guessing why their resume doesn't get callbacks. HR teams waste hours manually screening hundreds of applications. Current tools give vague scores with no actionable guidance. This platform gives exact, section-level feedback, rewrites weak bullets, and ranks candidates automatically.

**Target users:** Individual job seekers (B2C), HR managers & recruiters (B2B), companies integrating via API (developer tier).

**Core value proposition:** Unlike generic ATS checkers, this system combines BERT semantic similarity, TF-IDF lexical matching, and LLM-as-judge scoring — with role-specific weighting across 8 job families — to give the most accurate, actionable match analysis available.

---

## ⚠️ AGENT INSTRUCTIONS — READ BEFORE WRITING A SINGLE LINE

1. **Read all 15 sections completely before writing any code**
2. **Follow phases in strict sequence** — never begin Phase N+1 until Phase N is 100% complete with passing tests
3. **After each phase**, output a phase completion report (format defined in Section 15)
4. **Never invent features** not in this spec
5. **Never use `print()` for debugging** — use structured logging (structlog) everywhere
6. **Every function must have a corresponding pytest test** before the phase is marked complete
7. **Remove all debug statements** (`print("DEBUG:", ...)`) — none may exist in any file
8. **If a better approach exists**, implement it, document the deviation in the phase report, and proceed
9. **All secrets** come from environment variables only — never hardcoded
10. **Context preservation**: when approaching 80% of context window, emit the CONTEXT SUMMARY block from Section 14 before stopping

---

## Assumptions

- Python 3.11+ backend (FastAPI), React 18 + TypeScript frontend
- PostgreSQL 15 as primary database, Redis 7 for caching and queues
- Celery for async task processing (BERT encoding, LLM calls)
- Authentication via JWT (access + refresh tokens), optional Google OAuth2
- File storage: local disk for dev, AWS S3 (or compatible) for production
- AI providers: Anthropic Claude API for LLM scoring/rewriting, SentenceTransformers (all-MiniLM-L6-v2) for BERT embeddings, spaCy en_core_web_md for NLP
- Deployment target: Docker + docker-compose (local), AWS ECS or Railway (production)
- Email: SendGrid for transactional email
- Monitoring: Sentry (errors), structlog (structured logs), Prometheus + Grafana (metrics)
- Multi-tenancy: row-level tenant_id isolation (not separate schemas)
- Billing: Stripe for subscription tiers (Free / Pro / Enterprise)
- Three user roles: `job_seeker`, `recruiter`, `admin`

---

## Section 1 — Project Identity & File Structure

### Required Top-Level Directory Layout

```
ai-resume-matcher/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── config.py                # pydantic-settings config
│   │   ├── database.py              # SQLAlchemy async engine
│   │   ├── dependencies.py          # FastAPI dependency injection
│   │   ├── middleware.py            # CORS, logging, rate-limit middleware
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py        # Aggregates all v1 routers
│   │   │   │   ├── auth.py          # /auth endpoints
│   │   │   │   ├── resumes.py       # /resumes endpoints
│   │   │   │   ├── jobs.py          # /jobs endpoints
│   │   │   │   ├── matches.py       # /matches endpoints
│   │   │   │   ├── rewriter.py      # /rewriter endpoints
│   │   │   │   ├── users.py         # /users endpoints
│   │   │   │   ├── tenants.py       # /tenants endpoints (admin)
│   │   │   │   └── billing.py       # /billing endpoints
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── tenant.py
│   │   │   ├── resume.py
│   │   │   ├── job_description.py
│   │   │   ├── match_result.py
│   │   │   ├── rewrite_session.py
│   │   │   └── subscription.py
│   │   │
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── match.py
│   │   │   ├── rewriter.py
│   │   │   └── user.py
│   │   │
│   │   ├── services/                # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── match_service.py
│   │   │   ├── rewriter_service.py
│   │   │   ├── parser_service.py
│   │   │   ├── keyword_service.py
│   │   │   ├── role_score_service.py
│   │   │   ├── notification_service.py
│   │   │   └── billing_service.py
│   │   │
│   │   ├── ml/                      # All ML/AI logic isolated here
│   │   │   ├── __init__.py
│   │   │   ├── bert_encoder.py      # SentenceTransformer wrapper (lazy load, singleton)
│   │   │   ├── tfidf_scorer.py      # TF-IDF cosine similarity
│   │   │   ├── keyword_extractor.py # spaCy NLP + hard/soft skill matching
│   │   │   ├── llm_scorer.py        # Claude API as judge (structured output)
│   │   │   ├── role_detector.py     # 8-role profile + weight detection
│   │   │   ├── section_parser.py    # Section-level resume parsing
│   │   │   └── skill_graph.py       # Skill ontology / synonym resolution
│   │   │
│   │   ├── workers/                 # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── match_tasks.py       # async match pipeline
│   │   │   ├── rewrite_tasks.py     # async bullet rewrite
│   │   │   └── notification_tasks.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py            # structlog configuration
│   │       ├── security.py          # JWT, bcrypt helpers
│   │       ├── file_utils.py        # S3 upload, magic-byte validation
│   │       └── cache.py             # Redis client + decorators
│   │
│   ├── migrations/                  # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── conftest.py              # pytest fixtures, test DB, mock redis
│   │   ├── unit/
│   │   │   ├── test_parser.py
│   │   │   ├── test_keywords.py
│   │   │   ├── test_matcher.py
│   │   │   ├── test_role_detector.py
│   │   │   ├── test_rewriter.py
│   │   │   └── test_security.py
│   │   └── integration/
│   │       ├── test_auth_api.py
│   │       ├── test_resume_api.py
│   │       ├── test_match_api.py
│   │       └── test_billing_api.py
│   │
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── alembic.ini
│   └── pyproject.toml               # ruff, pytest, coverage config
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js 14 App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx             # Landing page
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx         # User dashboard
│   │   │   │   ├── resumes/page.tsx
│   │   │   │   ├── matches/page.tsx
│   │   │   │   └── settings/page.tsx
│   │   │   ├── match/
│   │   │   │   ├── new/page.tsx     # Upload + JD wizard
│   │   │   │   └── [id]/page.tsx    # Match result detail
│   │   │   ├── rewrite/
│   │   │   │   └── [id]/page.tsx    # Bullet rewriter UI
│   │   │   └── admin/
│   │   │       └── page.tsx         # Admin dashboard (role-gated)
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui base components
│   │   │   ├── resume/
│   │   │   │   ├── UploadZone.tsx
│   │   │   │   ├── ScoreCard.tsx
│   │   │   │   ├── KeywordBadges.tsx
│   │   │   │   └── SectionBreakdown.tsx
│   │   │   ├── match/
│   │   │   │   ├── MatchWizard.tsx
│   │   │   │   ├── ScoreGauge.tsx
│   │   │   │   └── FeedbackPanel.tsx
│   │   │   ├── rewriter/
│   │   │   │   ├── BulletCard.tsx
│   │   │   │   └── DiffView.tsx
│   │   │   └── layout/
│   │   │       ├── Navbar.tsx
│   │   │       └── Sidebar.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useMatch.ts
│   │   │   ├── useResume.ts
│   │   │   └── useJobPoller.ts      # Poll for async match result
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios client with JWT interceptor
│   │   │   ├── auth.ts              # Token storage (httpOnly cookie)
│   │   │   └── utils.ts
│   │   │
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript types
│   │
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── docker-compose.yml               # Full local stack
├── docker-compose.test.yml          # Ephemeral test stack
├── .github/
│   └── workflows/
│       ├── pr-checks.yml
│       └── deploy.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Section 2 — Tech Stack

| Layer | Choice | Why for this project |
|---|---|---|
| Backend framework | FastAPI (Python 3.11) | Async-native; auto OpenAPI docs; Pydantic validation built-in; replaces Flask |
| ORM | SQLAlchemy 2.0 async | Async sessions prevent blocking during BERT encoding; typed models |
| Database | PostgreSQL 15 | Row-level security for multi-tenancy; JSONB for flexible score storage |
| Migrations | Alembic | Native SQLAlchemy integration; version-controlled schema changes |
| Caching | Redis 7 | Embedding cache (content hash → vector); task queue broker; rate limit counters |
| Task queue | Celery 5 | BERT encoding (8s+) must be async; LLM calls non-blocking |
| PDF parsing | pdfplumber | Preserves layout and table structure; vastly superior to PyPDF2 |
| OCR fallback | pytesseract + Pillow | Handles scanned/image-based PDFs |
| BERT embeddings | sentence-transformers (all-MiniLM-L6-v2) | Fast, accurate semantic similarity; lazy-loaded singleton |
| NLP | spaCy en_core_web_md | Named entity recognition + noun chunk extraction |
| LLM scoring | Anthropic Claude API (claude-sonnet-4-20250514) | Structured JSON output for LLM-as-judge scoring; soft skill evaluation |
| Authentication | python-jose + passlib[bcrypt] | JWT access/refresh tokens; secure password hashing |
| File storage | boto3 (S3-compatible) | Resume files never stored on app disk in production |
| Frontend | Next.js 14 (App Router) + TypeScript | SSR for SEO; RSC reduces JS bundle; type safety end-to-end |
| Styling | Tailwind CSS + shadcn/ui | Rapid UI; accessible components; dark mode |
| State management | TanStack Query (React Query) | Server state + polling for async match jobs; caching |
| HTTP client | Axios | Interceptors for JWT refresh; consistent error handling |
| Email | SendGrid | Transactional email for match-complete notifications |
| Payments | Stripe | Subscription billing with webhook handler |
| Error tracking | Sentry | Both backend (Python SDK) and frontend (Next.js SDK) |
| Structured logging | structlog | JSON logs with trace_id, user_id, duration_ms |
| Metrics | Prometheus + Grafana | p95 latency, queue depth, match volume |
| Linting | ruff (Python), ESLint + Prettier (TS) | Fastest Python linter; strict TypeScript |
| Testing | pytest + httpx (backend), Vitest + Playwright (frontend) | Async-compatible; E2E coverage |
| Containerization | Docker + docker-compose | Reproducible local stack; same image to prod |
| CI/CD | GitHub Actions | PR gates + deployment pipeline |

---

## Section 3 — Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────────┐          ┌──────────────────────────────┐ │
│  │  Next.js 14 App  │          │   External API consumers     │ │
│  │  (React, TS)     │          │   (ATS systems, B2B clients) │ │
│  └────────┬─────────┘          └──────────────┬───────────────┘ │
└───────────┼───────────────────────────────────┼─────────────────┘
            │ HTTPS                              │ HTTPS + API Key
            ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Auth Router │  │ Match Router │  │  Rewrite / User / etc  │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬────────────┘  │
│         │                │                       │               │
│  ┌──────▼──────────────────────────────────────▼────────────┐  │
│  │                   Service Layer                            │  │
│  │  AuthService  MatchService  RewriterService  UserService  │  │
│  └──────┬──────────────────┬───────────────────┬────────────┘  │
│         │                  │                   │                 │
│  ┌──────▼──────┐    ┌──────▼──────┐   ┌───────▼──────────────┐ │
│  │  SQLAlchemy │    │  ML Layer   │   │   Celery Task Queue   │ │
│  │  (async)    │    │  (inline or │   │   (heavy work goes    │ │
│  └──────┬──────┘    │   queued)   │   │    here always)       │ │
│         │           └──────┬──────┘   └───────┬──────────────┘ │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────────┐  ┌──────────────────────┐
│  PostgreSQL  │   │  ML / AI Stack   │  │   Redis              │
│  (primary)   │   │                  │  │  ┌────────────────┐  │
│              │   │  ┌────────────┐  │  │  │ Task broker    │  │
│  ┌────────┐  │   │  │ pdfplumber │  │  │  ├────────────────┤  │
│  │users   │  │   │  │ spaCy NLP  │  │  │  │ Embedding cache│  │
│  │resumes │  │   │  │ BERT model │  │  │  ├────────────────┤  │
│  │jobs    │  │   │  │ TF-IDF     │  │  │  │ Rate limit ctrs│  │
│  │matches │  │   │  │ Claude API │  │  │  └────────────────┘  │
│  │tenants │  │   │  └────────────┘  │  └──────────────────────┘
│  └────────┘  │   └──────────────────┘
└──────────────┘              │
                              ▼
                   ┌─────────────────────┐
                   │  External Services   │
                   │  Anthropic Claude    │
                   │  SendGrid            │
                   │  Stripe              │
                   │  AWS S3              │
                   └─────────────────────┘
```

### Component Responsibilities

**FastAPI Backend** — Handles all HTTP routing, request validation via Pydantic schemas, authentication middleware, rate limiting, and delegates business logic to the service layer. Never contains ML or database logic directly in route handlers.

**Service Layer** — Pure Python business logic. Each service is stateless and injected via FastAPI's `Depends()`. Services call ML functions and database models but never import from each other (to prevent circular deps).

**ML Layer** (`app/ml/`) — All AI/ML logic isolated here. BERT model is a lazy-loaded module-level singleton (loaded once on first call, never reloaded). All ML functions are pure functions: input text → output score/keywords. No side effects, no DB calls.

**Celery Workers** — Process all long-running tasks: BERT encoding (~2-8s), LLM API calls (~3-15s), email sending. Workers read from Redis queue, write results to PostgreSQL, then mark the job as complete. The HTTP endpoint returns a `job_id` immediately and the client polls `/matches/{job_id}/status`.

**PostgreSQL** — Single source of truth for all persistent data. Uses async SQLAlchemy sessions. Row-level `tenant_id` on all tables that support multi-tenancy.

**Redis** — Dual purpose: (1) Celery broker and result backend; (2) embedding cache keyed by SHA-256 hash of text content — prevents re-encoding identical text.

### End-to-End Request Flow (Match Creation)

```
1. User submits POST /api/v1/matches (resume file + JD text)
2. JWT middleware validates token → injects user object
3. Rate limiter checks Redis: user's match count in last hour
4. ResumeService validates file: extension check + magic bytes check (not just extension)
5. File uploaded to S3; S3 key stored in DB
6. MatchResult record created in PostgreSQL with status="pending", job_id returned
7. Celery task dispatched: match_tasks.run_match_pipeline.delay(match_id)
8. HTTP response: 202 Accepted { "match_id": "uuid", "status": "pending" }
9. Client polls GET /api/v1/matches/{match_id}/status every 2 seconds
10. [WORKER] pdfplumber extracts text + sections from resume
11. [WORKER] spaCy + skill graph extracts hard/soft skills
12. [WORKER] Check Redis cache: SHA-256(resume_text) → embedding exists?
13. [WORKER] If cache miss: BERT encodes resume + JD, stores in Redis (TTL 24h)
14. [WORKER] TF-IDF score computed (fast, in-memory)
15. [WORKER] Keyword overlap score computed
16. [WORKER] Role detector identifies job family (tech/finance/etc)
17. [WORKER] role_score_service applies role-weighted final score
18. [WORKER] LLM scorer sends resume + JD to Claude API → structured JSON verdict
19. [WORKER] All scores merged → MatchResult updated in DB with status="complete"
20. [WORKER] Notification task dispatched: email user "Your match is ready"
21. Client polls → gets 200 with full result
```

### Communication Patterns

- **HTTP REST** for all client ↔ backend communication. Versioned at `/api/v1/`. JSON only.
- **Celery tasks** (Redis broker) for backend ↔ worker communication. Never HTTP between services.
- **WebSocket** (optional Phase 3 enhancement): real-time status push instead of polling. Use FastAPI's built-in WebSocket support.
- **Webhooks** (incoming): Stripe sends billing events to `/api/v1/billing/webhook`.

### Monolith vs Microservices Decision

**Monolith** — a single FastAPI application with Celery workers. Reasoning: the project has one team, one codebase, and shared database access between the API and ML layer. Microservices would add network overhead and deployment complexity with no benefit at this scale. The ML layer is isolated in `app/ml/` so it CAN be extracted to a separate service later without refactoring business logic.

---

## Section 4 — Database Design

### Tables

```sql
TABLE: tenants
  id              UUID          PK, default gen_random_uuid()
  name            VARCHAR(255)  NOT NULL
  slug            VARCHAR(100)  UNIQUE NOT NULL
  plan            ENUM          ['free','pro','enterprise'] DEFAULT 'free'
  api_key_hash    VARCHAR(255)  NULL  -- hashed API key for B2B access
  created_at      TIMESTAMPTZ   DEFAULT now()
  deleted_at      TIMESTAMPTZ   NULL

TABLE: users
  id              UUID          PK, default gen_random_uuid()
  tenant_id       UUID          FK → tenants.id NOT NULL
  email           VARCHAR(255)  UNIQUE NOT NULL
  password_hash   VARCHAR(255)  NULL  -- null if OAuth-only user
  role            ENUM          ['job_seeker','recruiter','admin'] DEFAULT 'job_seeker'
  full_name       VARCHAR(150)  NOT NULL
  is_verified     BOOLEAN       DEFAULT false
  google_id       VARCHAR(255)  NULL UNIQUE
  created_at      TIMESTAMPTZ   DEFAULT now()
  last_login_at   TIMESTAMPTZ   NULL
  deleted_at      TIMESTAMPTZ   NULL

TABLE: refresh_tokens
  id              UUID          PK
  user_id         UUID          FK → users.id ON DELETE CASCADE
  token_hash      VARCHAR(255)  NOT NULL UNIQUE
  expires_at      TIMESTAMPTZ   NOT NULL
  revoked_at      TIMESTAMPTZ   NULL
  created_at      TIMESTAMPTZ   DEFAULT now()

TABLE: resumes
  id              UUID          PK
  user_id         UUID          FK → users.id
  tenant_id       UUID          FK → tenants.id
  filename        VARCHAR(255)  NOT NULL
  s3_key          VARCHAR(500)  NOT NULL
  file_size_bytes INTEGER       NOT NULL
  mime_type       VARCHAR(50)   NOT NULL  -- 'application/pdf' or docx
  parsed_text     TEXT          NULL      -- extracted after upload
  parsed_sections JSONB         NULL      -- {"experience": "...", "education": "..."}
  parse_status    ENUM          ['pending','done','failed'] DEFAULT 'pending'
  created_at      TIMESTAMPTZ   DEFAULT now()
  deleted_at      TIMESTAMPTZ   NULL

TABLE: job_descriptions
  id              UUID          PK
  user_id         UUID          FK → users.id
  tenant_id       UUID          FK → tenants.id
  title           VARCHAR(255)  NULL
  company         VARCHAR(255)  NULL
  raw_text        TEXT          NOT NULL
  parsed_data     JSONB         NULL  -- {required_skills, nice_to_have, experience_level, salary}
  source_url      VARCHAR(500)  NULL
  created_at      TIMESTAMPTZ   DEFAULT now()

TABLE: match_results
  id              UUID          PK
  user_id         UUID          FK → users.id
  tenant_id       UUID          FK → tenants.id
  resume_id       UUID          FK → resumes.id
  job_id          UUID          FK → job_descriptions.id
  status          ENUM          ['pending','processing','complete','failed'] DEFAULT 'pending'
  celery_task_id  VARCHAR(255)  NULL
  bert_score      NUMERIC(5,2)  NULL
  tfidf_score     NUMERIC(5,2)  NULL
  keyword_score   NUMERIC(5,2)  NULL
  llm_score       NUMERIC(5,2)  NULL
  final_score     NUMERIC(5,2)  NULL
  role_detected   VARCHAR(50)   NULL  -- 'tech','finance','marketing' etc
  weights_used    JSONB         NULL  -- {"bert":0.45,"tfidf":0.35,"keyword":0.20}
  score_breakdown JSONB         NULL  -- per-score contributions
  matched_keywords JSONB        NULL  -- array of matched skill strings
  missing_keywords JSONB        NULL  -- array of missing skill strings
  section_scores  JSONB         NULL  -- {"experience":82,"education":71,...}
  llm_verdict     JSONB         NULL  -- full Claude API structured response
  feedback_text   TEXT          NULL  -- human-readable summary
  error_message   TEXT          NULL  -- if status='failed'
  processing_ms   INTEGER       NULL  -- total pipeline duration
  created_at      TIMESTAMPTZ   DEFAULT now()
  completed_at    TIMESTAMPTZ   NULL

TABLE: rewrite_sessions
  id              UUID          PK
  user_id         UUID          FK → users.id
  match_id        UUID          FK → match_results.id NULL
  resume_id       UUID          FK → resumes.id
  jd_text         TEXT          NOT NULL
  status          ENUM          ['pending','complete','failed']
  celery_task_id  VARCHAR(255)  NULL
  bullet_count    INTEGER       NULL
  weak_count      INTEGER       NULL
  rewrites        JSONB         NULL  -- array of {original, rewritten_variants:[x3], reason}
  created_at      TIMESTAMPTZ   DEFAULT now()

TABLE: subscriptions
  id              UUID          PK
  tenant_id       UUID          FK → tenants.id UNIQUE
  stripe_customer_id    VARCHAR(255) NOT NULL
  stripe_subscription_id VARCHAR(255) NULL
  plan            ENUM          ['free','pro','enterprise']
  status          ENUM          ['active','canceled','past_due','trialing']
  current_period_end    TIMESTAMPTZ NULL
  created_at      TIMESTAMPTZ   DEFAULT now()
  updated_at      TIMESTAMPTZ   DEFAULT now()

TABLE: usage_events
  id              UUID          PK
  tenant_id       UUID          FK → tenants.id
  user_id         UUID          FK → users.id NULL
  event_type      VARCHAR(100)  NOT NULL  -- 'match_created','rewrite_created'
  metadata        JSONB         NULL
  created_at      TIMESTAMPTZ   DEFAULT now()
```

### Indexes

```sql
-- users
CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;

-- resumes
CREATE INDEX idx_resumes_user ON resumes(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_resumes_tenant ON resumes(tenant_id);

-- match_results
CREATE INDEX idx_matches_user ON match_results(user_id);
CREATE INDEX idx_matches_tenant ON match_results(tenant_id);
CREATE INDEX idx_matches_status ON match_results(status) WHERE status IN ('pending','processing');
CREATE INDEX idx_matches_created ON match_results(created_at DESC);

-- usage_events
CREATE INDEX idx_usage_tenant_type ON usage_events(tenant_id, event_type, created_at DESC);

-- refresh_tokens
CREATE INDEX idx_refresh_token_hash ON refresh_tokens(token_hash) WHERE revoked_at IS NULL;
```

### Relationships

| From | Relationship | To | Notes |
|---|---|---|---|
| users | many-to-one | tenants | Every user belongs to one tenant |
| resumes | many-to-one | users | A user can have many saved resumes |
| job_descriptions | many-to-one | users | A user can save many JDs |
| match_results | many-to-one | users | User can run many matches |
| match_results | many-to-one | resumes | One resume per match |
| match_results | many-to-one | job_descriptions | One JD per match |
| rewrite_sessions | many-to-one | match_results | Optional link to a match |
| subscriptions | one-to-one | tenants | One subscription per tenant |

### Soft Delete Strategy

All user-owned content uses `deleted_at TIMESTAMPTZ NULL`. Hard deletes never happen in application code. Add `WHERE deleted_at IS NULL` to all queries via a SQLAlchemy query filter applied at the session level.

### Migration Convention

Alembic, named `YYYY_MM_DD_HHMM_description.py`. Run migrations before app startup in CI. Never edit existing migrations — always add new ones.

### Seed Data

On fresh setup, create: one `tenants` row (name="Default", plan="free"), one `users` row (role="admin", email from env var `ADMIN_EMAIL`, password from `ADMIN_PASSWORD`).

---

## Section 5 — API Design

All routes prefixed with `/api/v1/`. All protected routes require `Authorization: Bearer <token>` header. All responses use consistent envelope:

```json
{ "data": {...}, "error": null }   // success
{ "data": null, "error": { "code": "string", "message": "string" } }  // error
```

```
MODULE: Health
  GET  /health                     → Liveness check           Auth: public
    res: { "status": "ok", "db": "ok", "redis": "ok", "version": "1.0.0" }

MODULE: Auth
  POST /api/v1/auth/register       → Register user            Auth: public
    req:  { email, password, full_name, tenant_slug? }
    res:  { user: { id, email, role }, access_token, refresh_token }
    err:  409 email_taken | 422 validation_error

  POST /api/v1/auth/login          → Login                    Auth: public
    req:  { email, password }
    res:  { access_token, refresh_token, user }
    err:  401 invalid_credentials | 429 rate_limited

  POST /api/v1/auth/refresh        → Refresh access token     Auth: public
    req:  { refresh_token }
    res:  { access_token, refresh_token }
    err:  401 token_invalid | 401 token_expired

  POST /api/v1/auth/logout         → Revoke refresh token     Auth: any user
    req:  { refresh_token }
    res:  { success: true }

  GET  /api/v1/auth/me             → Current user info        Auth: any user
    res:  { user: { id, email, role, full_name, tenant } }

  POST /api/v1/auth/google         → Google OAuth callback    Auth: public
    req:  { code, redirect_uri }
    res:  { access_token, refresh_token, user }

MODULE: Resumes
  POST /api/v1/resumes             → Upload resume            Auth: job_seeker
    req:  multipart/form-data: { file: PDF/DOCX (max 10MB) }
    res:  { resume: { id, filename, parse_status, created_at } }
    err:  400 invalid_file_type | 413 file_too_large | 422 magic_byte_mismatch

  GET  /api/v1/resumes             → List user's resumes      Auth: job_seeker
    res:  { resumes: [{ id, filename, parse_status, created_at }] }

  GET  /api/v1/resumes/{id}        → Get resume detail        Auth: job_seeker (own)
    res:  { resume: { id, filename, parsed_sections, created_at } }
    err:  404 not_found | 403 forbidden

  DELETE /api/v1/resumes/{id}      → Soft delete resume       Auth: job_seeker (own)
    res:  { success: true }
    err:  404 not_found | 403 forbidden

MODULE: Job Descriptions
  POST /api/v1/jobs                → Save a job description   Auth: any user
    req:  { raw_text, title?, company?, source_url? }
    res:  { job: { id, title, company, created_at } }

  GET  /api/v1/jobs                → List saved JDs           Auth: any user
    res:  { jobs: [{ id, title, company, created_at }] }

  GET  /api/v1/jobs/{id}           → Get JD detail            Auth: any user (own)
    res:  { job: { id, title, raw_text, parsed_data } }

MODULE: Matches
  POST /api/v1/matches             → Start a match            Auth: any user
    req:  { resume_id: UUID, job_id: UUID }
    res:  202 { match_id: UUID, status: "pending" }
    err:  402 usage_limit_exceeded | 404 resume_not_found | 404 job_not_found

  GET  /api/v1/matches/{id}        → Get match result         Auth: any user (own)
    res:  { match: { id, status, final_score, bert_score, tfidf_score,
                     keyword_score, llm_score, role_detected, weights_used,
                     matched_keywords, missing_keywords, section_scores,
                     feedback_text, llm_verdict, processing_ms, created_at } }
    err:  404 not_found | 403 forbidden

  GET  /api/v1/matches             → List user's matches      Auth: any user
    query: ?page=1&limit=20&status=complete
    res:  { matches: [...], total, page, limit }

MODULE: Rewriter
  POST /api/v1/rewriter            → Start bullet rewrite     Auth: any user
    req:  { resume_id: UUID, jd_text: string, match_id?: UUID }
    res:  202 { session_id: UUID, status: "pending" }
    err:  402 usage_limit_exceeded

  GET  /api/v1/rewriter/{session_id} → Get rewrite result    Auth: any user (own)
    res:  { session: { id, status, bullet_count, weak_count,
                       rewrites: [{ original, rewritten_variants:[str,str,str], reason }] } }

MODULE: Users
  GET  /api/v1/users/me            → Get profile              Auth: any user
    res:  { user: { id, email, full_name, role, subscription_plan } }

  PATCH /api/v1/users/me           → Update profile           Auth: any user
    req:  { full_name?, email? }
    res:  { user: { id, email, full_name } }

  PATCH /api/v1/users/me/password  → Change password          Auth: any user
    req:  { current_password, new_password }
    res:  { success: true }
    err:  401 wrong_current_password

MODULE: Admin (admin role required for all)
  GET  /api/v1/admin/users         → List all users           Auth: admin
    query: ?tenant_id=&page=&limit=
    res:  { users: [...], total }

  PATCH /api/v1/admin/users/{id}   → Update user role         Auth: admin
    req:  { role }
    res:  { user }

  GET  /api/v1/admin/tenants       → List all tenants         Auth: admin
    res:  { tenants: [...] }

  GET  /api/v1/admin/stats         → Platform analytics       Auth: admin
    res:  { total_users, total_matches, matches_today, avg_score }

MODULE: Billing
  POST /api/v1/billing/checkout    → Create Stripe checkout   Auth: any user
    req:  { plan: 'pro' | 'enterprise' }
    res:  { checkout_url: string }

  GET  /api/v1/billing/portal      → Stripe customer portal   Auth: any user
    res:  { portal_url: string }

  GET  /api/v1/billing/status      → Current plan status      Auth: any user
    res:  { plan, status, current_period_end, usage: { matches_used, matches_limit } }

  POST /api/v1/billing/webhook     → Stripe webhook handler   Auth: Stripe-Signature header
    req:  Stripe event payload
    res:  { received: true }
    err:  400 invalid_signature
```

---

## Section 6 — ML Pipeline (Detailed Implementation)

This section expands on what must be built inside `app/ml/`. Each module must be a pure function layer with no database or HTTP dependencies.

### 6.1 Resume Parser (`section_parser.py`)

Replace `PyPDF2` entirely. Use `pdfplumber` as primary extractor. Fall back to `pytesseract` OCR if pdfplumber returns fewer than 100 characters.

Extract and return a structured dict:
```python
{
  "full_text": str,
  "sections": {
    "contact": str,
    "summary": str,
    "experience": str,
    "education": str,
    "skills": str,
    "projects": str,
    "certifications": str,
    "other": str
  }
}
```

Section detection uses regex header matching (case-insensitive): `EXPERIENCE|WORK HISTORY`, `EDUCATION|ACADEMIC`, `SKILLS|TECHNICAL`, `PROJECTS|PORTFOLIO`, `CERTIFICATIONS|LICENSES`, `SUMMARY|OBJECTIVE|PROFILE`.

For DOCX files: use `python-docx`, iterate paragraphs and tables.

Magic-byte validation must happen BEFORE any parsing:
- PDF: first 4 bytes = `%PDF`
- DOCX: first 4 bytes = `PK\x03\x04` (ZIP format)
- Reject any file where bytes don't match the claimed extension

### 6.2 BERT Encoder (`bert_encoder.py`)

```python
# Singleton pattern — model loaded once at first call
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def encode_text(text: str) -> list[float]:
    """Returns embedding vector as list of floats."""

def compute_bert_score(resume_text: str, jd_text: str, redis_client) -> float:
    """
    1. SHA-256 hash both texts concatenated
    2. Check Redis cache for this hash
    3. If cache hit: return cached score
    4. If cache miss: encode both, compute cosine similarity, cache result (TTL=86400)
    5. Return float 0.0-100.0
    """
```

### 6.3 Keyword Extractor (`keyword_extractor.py`)

Keep the existing HARD_SKILLS and SOFT_SKILLS sets from the original project, AND add:

**Skill Graph / Synonym Resolution** (`skill_graph.py`): A dictionary mapping skill aliases to canonical forms:
```python
SKILL_ALIASES = {
    "nodejs": "node.js",
    "node": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "scikit": "scikit-learn",
    "sklearn": "scikit-learn",
    "gpt": "openai",
    "llm": "large language models",
    # ... extend comprehensively
}

SKILL_IMPLIES = {
    "react": ["javascript"],
    "pytorch": ["python", "machine learning"],
    "tensorflow": ["python", "machine learning"],
    "django": ["python"],
    "fastapi": ["python"],
    "kubernetes": ["docker"],
    # ... extend comprehensively
}
```

Before keyword matching, normalize all skills through `SKILL_ALIASES`. When computing matched keywords, also credit implied skills from `SKILL_IMPLIES`.

### 6.4 LLM Scorer (`llm_scorer.py`)

Use the Anthropic Claude API. The prompt must request structured JSON output:

```python
SYSTEM_PROMPT = """You are an expert technical recruiter and resume evaluator.
Analyze the given resume against the job description and return ONLY valid JSON.
No preamble, no markdown, no explanation outside the JSON."""

USER_PROMPT = """
RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return this exact JSON structure:
{{
  "overall_fit": <integer 0-100>,
  "experience_match": <integer 0-100>,
  "skills_match": <integer 0-100>,
  "soft_skills_match": <integer 0-100>,
  "seniority_match": <integer 0-100>,
  "strengths": [<string>, <string>, <string>],
  "gaps": [<string>, <string>, <string>],
  "recommendation": "<strong_match|good_match|partial_match|weak_match>",
  "one_line_summary": "<string max 200 chars>"
}}"""
```

Parse the JSON response. On `json.JSONDecodeError`, retry once with a stricter prompt. On second failure, return `None` and log the error — never crash the pipeline because the LLM scorer failed.

### 6.5 Role Detector (`role_detector.py`)

Keep all 8 existing role profiles from `role_score.py` exactly as implemented. Add two new roles:

```python
"legal": {
    "label": "Legal / Compliance",
    "icon": "⚖️",
    "weights": {"bert": 0.45, "tfidf": 0.30, "keyword": 0.25},
    "keywords": ["attorney", "counsel", "litigation", "compliance", "regulatory",
                 "contract", "legal", "paralegal", "gdpr", "hipaa", "soc2", ...]
},
"operations": {
    "label": "Operations / Supply Chain",
    "icon": "🔧",
    "weights": {"bert": 0.40, "tfidf": 0.35, "keyword": 0.25},
    "keywords": ["operations", "supply chain", "logistics", "procurement",
                 "inventory", "vendor", "process improvement", "six sigma", ...]
}
```

### 6.6 Final Score Computation

```python
def compute_final_score(bert: float, tfidf: float, keyword: float,
                        llm: float | None, weights: dict) -> float:
    """
    If LLM score available: blend 4 scores
      final = bert*w_bert + tfidf*w_tfidf + keyword*w_keyword + llm*0.15
      (reduce other weights proportionally to accommodate 15% LLM weight)
    If LLM unavailable: use 3-score formula from role weights only
    Always return float 0.0 to 100.0, rounded to 1 decimal place.
    """
```

---

## Section 7 — Security Architecture

### Authentication

- **Access token**: JWT, signed with RS256 (asymmetric), expires in 15 minutes
- **Refresh token**: opaque random 32-byte hex, stored as bcrypt hash in `refresh_tokens` table, expires in 30 days
- **Refresh rotation**: every refresh call issues a new refresh token and revokes the old one
- **Storage (frontend)**: access token in memory only (React state); refresh token in `httpOnly; Secure; SameSite=Strict` cookie
- **No localStorage** for any token — prevents XSS token theft

### Authorization (RBAC)

| Permission | job_seeker | recruiter | admin |
|---|---|---|---|
| Upload own resume | ✅ | ✅ | ✅ |
| Run match on own data | ✅ | ✅ | ✅ |
| View own matches | ✅ | ✅ | ✅ |
| Batch upload resumes | ❌ | ✅ | ✅ |
| View all tenant users | ❌ | ✅ | ✅ |
| View all tenant matches | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| View all tenants | ❌ | ❌ | ✅ |
| Access admin stats | ❌ | ❌ | ✅ |

Implement via FastAPI `Depends()` — e.g., `get_current_user_with_role("admin")`.

### Input Validation

- All request bodies validated by Pydantic schemas before reaching service layer
- File uploads: validate extension AND magic bytes (first N bytes)
- Max file size: 10MB enforced at nginx/gateway level AND in FastAPI middleware
- JD text: max 50,000 characters; strip all HTML tags before storage
- No raw SQL anywhere — SQLAlchemy ORM only

### Rate Limiting

Use `slowapi` (FastAPI rate limiting library):

| Endpoint | Limit | Window |
|---|---|---|
| POST /auth/login | 10 requests | 15 minutes per IP |
| POST /auth/register | 5 requests | 1 hour per IP |
| POST /matches | 10 matches | 1 hour per user (free plan) |
| POST /matches | 100 matches | 1 hour per user (pro plan) |
| POST /rewriter | 5 sessions | 1 hour per user (free plan) |
| All other endpoints | 200 requests | 1 minute per user |

### CORS

Allow only: `FRONTEND_URL` env var (e.g., `https://app.resumematcher.com`). Never `*` in production.

### Secret Management

All secrets in environment variables. Never in source code. In production, use AWS SSM Parameter Store or Doppler. Required env vars validated at startup via pydantic-settings — app refuses to start if any required secret is missing.

### File Security

- Uploaded files never executed — stored in S3 with no public URL
- Presigned S3 URLs generated on demand (expire in 15 minutes)
- File content validated before parsing: magic bytes checked, file size re-checked after upload
- Virus scanning: integrate ClamAV or S3 event + Lambda for async scanning (optional, mark as deferred for Phase 1, implement in Phase 4)

### OWASP Top 10 Checklist

| Risk | Mitigation |
|---|---|
| A01 Broken Access Control | RBAC on all routes; owner checks on all data reads |
| A02 Cryptographic Failures | RS256 JWT; bcrypt for passwords; TLS 1.3; S3 SSE |
| A03 Injection | SQLAlchemy ORM only; Pydantic input validation |
| A04 Insecure Design | Threat model documented; auth tested |
| A05 Security Misconfiguration | Pydantic-settings validates all secrets at startup |
| A06 Vulnerable Components | Dependabot + `pip audit` in CI |
| A07 Authentication Failures | Rate limits on auth; refresh rotation; short access token TTL |
| A08 Software/Data Integrity | Docker image SHA pinned in CI |
| A09 Logging Failures | structlog JSON logs; no secrets in logs; Sentry |
| A10 SSRF | No user-supplied URLs fetched server-side (except scraping, isolated) |

---

## Section 8 — Code Quality Standards

### Python Standards

- Python 3.11+ type hints on ALL function signatures — no `Any` unless justified with a comment
- Max function length: 40 lines. If longer, extract helpers.
- Max file length: 400 lines. If longer, split the module.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- All async functions use `async def` — no blocking calls inside async functions (no `requests`, use `httpx`)
- No global mutable state except the BERT model singleton (documented exception)
- Every function has a docstring if it has non-obvious behavior
- `ruff` linting + formatting, configured in `pyproject.toml`

### TypeScript Standards

- Strict mode enabled in `tsconfig.json` (`"strict": true`)
- No `any` type — use `unknown` and narrow it
- All API response types defined in `src/types/index.ts`
- React components: functional only, no class components
- `useEffect` dependencies must be complete — ESLint `exhaustive-deps` rule enabled

### Import Rules

- Backend: `app.ml` modules may NOT import from `app.api` or `app.services`
- Backend: `app.api` routers may NOT import from each other
- Backend: `app.services` are the only layer that import from `app.ml`
- Frontend: no component imports from `app/` directory (only from `components/` and `lib/`)

---

## Section 9 — Testing Requirements

### Backend (pytest)

```
tests/
  conftest.py          — AsyncClient, test PostgreSQL (separate DB), mock Redis, mock S3
  unit/
    test_parser.py     — pdfplumber extraction, section detection, magic byte validation
    test_keywords.py   — hard skill matching, soft skill matching, skill alias resolution
    test_matcher.py    — TF-IDF score, BERT score (mock model), keyword overlap score
    test_role_detector.py — role detection for all 10 role profiles
    test_llm_scorer.py — mock Claude API response, JSON parsing, retry on failure
    test_rewriter.py   — bullet extraction, strength scoring, rewrite variants
    test_security.py   — JWT creation/validation, bcrypt hashing, refresh rotation
  integration/
    test_auth_api.py   — register, login, refresh, logout, me endpoint
    test_resume_api.py — upload (valid PDF, invalid type, too large), list, delete
    test_match_api.py  — create match, poll status, get result, list matches
    test_billing_api.py — checkout, portal, webhook signature validation
```

**Coverage target: 85% minimum**. CI blocks merge below this threshold.

### Frontend (Vitest + Playwright)

- Unit tests for all custom hooks (`useMatch`, `useResume`, `useJobPoller`)
- Component tests for `ScoreCard`, `UploadZone`, `BulletCard`
- E2E tests (Playwright): register → upload resume → paste JD → view match result → view rewrite

### Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=85"

[tool.coverage.run]
omit = ["tests/*", "migrations/*", "app/main.py"]
```

---

## Section 10 — Logging & Monitoring

### Logging Setup (`app/utils/logger.py`)

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

Every log entry must include: `trace_id`, `user_id` (if authenticated), `event`, `duration_ms` (for timed operations).

Generate `trace_id` in middleware on every request, bind to structlog context.

**Never log**: passwords, tokens, full resume text (log resume_id only), PII beyond user_id.

### Log Events Required

| Event | Level | When |
|---|---|---|
| `user.register` | INFO | Successful registration |
| `user.login` | INFO | Successful login |
| `user.login_failed` | WARN | Bad credentials |
| `match.created` | INFO | Match job dispatched |
| `match.complete` | INFO | Pipeline finished; include final_score, processing_ms |
| `match.failed` | ERROR | Pipeline exception; include error type |
| `ml.bert.cache_hit` | DEBUG | Embedding found in Redis |
| `ml.bert.cache_miss` | DEBUG | Embedding computed fresh |
| `ml.llm.called` | INFO | Claude API called; include latency |
| `ml.llm.failed` | WARN | Claude returned invalid JSON; falling back |
| `file.upload` | INFO | Resume uploaded; include file_size |
| `file.rejected` | WARN | Invalid file type or magic bytes |
| `billing.subscription_updated` | INFO | Stripe webhook processed |
| `rate_limit.exceeded` | WARN | User hit rate limit |

### Metrics (Prometheus)

Expose `/metrics` endpoint (protected, internal only). Track:
- `http_request_duration_seconds` histogram (labels: method, path, status)
- `match_pipeline_duration_seconds` histogram
- `celery_queue_depth` gauge
- `bert_cache_hits_total` counter
- `bert_cache_misses_total` counter
- `llm_api_calls_total` counter (labels: success, failure)

### Alerting Rules

- Error rate > 1% over 5 minutes → Slack #alerts-critical
- p95 match pipeline > 30 seconds → Slack #alerts-warning  
- Celery queue depth > 50 → Slack #alerts-warning
- Redis memory > 80% → Slack #alerts-critical
- Any `match.failed` event with user-visible impact → Sentry

---

## Section 11 — CI/CD Pipeline

### `.github/workflows/pr-checks.yml`

```yaml
name: PR Checks
on: [pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: test_db }
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: ruff format --check .
      - run: pip-audit                      # fail on high/critical CVEs
      - run: pytest --cov --cov-fail-under=85
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm audit --audit-level=high
      - run: npm run test
      - run: npm run build
```

**PR merge is blocked if any step fails.**

### `.github/workflows/deploy.yml`

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - Build Docker image (backend + worker + frontend)
      - Tag with: git commit SHA
      - Push to container registry (GitHub Container Registry)
      - Deploy to staging environment
      - Run smoke tests against staging /health endpoint
      - Run Playwright E2E tests against staging
      - Notify Slack on success or failure
  deploy-production:
    needs: deploy-staging
    environment: production    # requires manual approval in GitHub
    steps:
      - Pull staging-tested image (SAME SHA — no rebuild)
      - Run Alembic migrations: alembic upgrade head
      - Deploy with rolling update (new containers up before old removed)
      - Run smoke tests: /health, POST /auth/login with test account
      - Auto-rollback if smoke tests fail within 5 minutes
      - Tag git commit as release
      - Update changelog
```

---

## Section 12 — Containerization

### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser
COPY --from=builder /install /usr/local
COPY . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `backend/Dockerfile.worker`

Same as backend Dockerfile but CMD is:
```dockerfile
CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
```

### `docker-compose.yml`

```yaml
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: resume_matcher
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  backend:
    build: ./backend
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
    env_file: .env
    ports:
      - "8000:8000"

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    depends_on:
      - backend
    env_file: .env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

volumes:
  pgdata:
```

### Environment Variables (`.env.example`)

```bash
# App
SECRET_KEY=                        # RS256 private key (PEM format)
PUBLIC_KEY=                        # RS256 public key (PEM format)
ENVIRONMENT=development            # development | staging | production
LOG_LEVEL=info
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/resume_matcher

# Redis
REDIS_URL=redis://redis:6379/0

# AI / ML
ANTHROPIC_API_KEY=                 # Claude API key
OPENROUTER_API_KEY=                # Fallback if Claude unavailable

# File Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=

# Email
SENDGRID_API_KEY=
FROM_EMAIL=noreply@resumematcher.com

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRO_PRICE_ID=
STRIPE_ENTERPRISE_PRICE_ID=

# Frontend
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**VALIDATION RULE**: At application startup, `app/config.py` (pydantic-settings) must validate every required env var. If any is missing, raise a clear error and refuse to start. Never silently use a None or empty string secret.

---

## Section 13 — Scalability Plan

### Caching Strategy

| What to cache | Key pattern | TTL | Invalidation |
|---|---|---|---|
| BERT embedding | `emb:{sha256_of_text}` | 24 hours | Never (content-addressed) |
| TF-IDF score | `tfidf:{hash_resume}:{hash_jd}` | 1 hour | On resume update |
| User profile | `user:{user_id}` | 15 minutes | On profile update |
| Match result | `match:{match_id}` | 5 minutes | On status change |
| Rate limit counter | `rl:{user_id}:{endpoint}` | 1 hour | TTL-based |

### Async Offloading — ALL of These MUST Go to Celery Workers

- BERT text encoding
- LLM (Claude API) calls
- Full match pipeline
- Bullet rewriting pipeline
- Email sending (SendGrid)
- Resume parsing (pdfplumber, OCR)
- S3 upload events
- Usage event recording

**The FastAPI HTTP handlers must return within 200ms.** If any operation takes longer than 200ms, it belongs in a Celery task.

### Stateless Confirmation Checklist

- [ ] No in-process session state — all user state in PostgreSQL + Redis
- [ ] No local file writes — uploaded files go directly to S3 (stream upload)
- [ ] BERT model is the only in-process state — acceptable (read-only, loaded once)
- [ ] Any instance can handle any request — horizontal scaling is safe

### Scale Triggers

| Metric | Threshold | Action |
|---|---|---|
| CPU > 70% for 5 min | Add one backend instance | Auto-scale |
| Celery queue > 50 tasks | Add one worker instance | Auto-scale |
| DB connections > 80% of pool | Add PgBouncer connection pooler | Manual |
| Redis memory > 80% | Increase Redis memory or add replica | Manual |
| p95 latency > 3s (HTTP) | Investigate; add caching or instance | Alert |

---

## Section 14 — Context Preservation Protocol

When the agent's context window approaches 80% capacity during a long build, it must stop at the nearest clean file boundary and emit this block:

```
## CONTEXT SUMMARY — {ISO_TIMESTAMP}

### Completed
- [List each completed file with relative path]
- [Each completed migration]
- [Each completed test file]

### In Progress
- Task:       [exact phase task name]
- File:       [relative/path/to/current_file.py]
- Status:     [what functions are done / what remains]
- Last line:  [exact last function or class name written]

### Pending (this phase)
- [Remaining files in current phase, in order]

### Pending (future phases)
- Phase X: [summary]
- Phase Y: [summary]

### Key Decisions Made
- [Any deviation from this SKILL.md, with reasoning]
- [Additional libraries added]
- [Schema changes]

### Exact Next Instruction
"Continue from {relative/path/to/file.py}:{function_or_class_name}.
Next task: {exact_task_name_from_phase_list}."
```

The user will paste this summary into a new chat session. The agent must resume exactly from the stated point. Do not re-examine or redo completed work.

---

## Section 15 — Build Phases & Agent Instructions

### Phase Completion Report Format

After completing each phase, output exactly:
```
## Phase {N} Complete — {Phase Name}
Files created: [{list}]
Tests passing: {count} / {total}
Coverage: {percent}%
Deviations from spec: {none | list with reasoning}
Ready to proceed: Phase {N+1}
```

---

### PHASE 1 — Foundation (Do This First)

**Goal**: A working FastAPI app with auth, PostgreSQL, and one working endpoint. No ML yet.

Tasks in order:
1. Create `backend/pyproject.toml` with ruff, pytest, coverage config
2. Create `backend/requirements.txt` with all dependencies pinned to specific versions
3. Create `backend/app/config.py` — pydantic-settings, validates all required env vars at startup
4. Create `backend/app/database.py` — async SQLAlchemy engine, session factory
5. Create all SQLAlchemy models (`app/models/*.py`) matching Section 4 exactly
6. Create `alembic.ini` + `migrations/env.py` — generate initial migration
7. Create `backend/app/utils/logger.py` — structlog JSON configuration
8. Create `backend/app/utils/security.py` — JWT RS256 sign/verify, bcrypt hash/verify
9. Create `backend/app/main.py` — FastAPI app factory, register middleware, include routers
10. Create `backend/app/middleware.py` — CORS, request logging with trace_id, rate limiter setup
11. Create `backend/app/api/v1/auth.py` — register, login, refresh, logout, me
12. Create `backend/app/schemas/auth.py` — Pydantic schemas for all auth endpoints
13. Create `backend/app/services/auth_service.py` — business logic for auth
14. Create `backend/app/dependencies.py` — `get_current_user`, `require_role` dependencies
15. Create `backend/app/api/v1/router.py` — aggregate all routers
16. Create `backend/Dockerfile` and `backend/Dockerfile.worker`
17. Create `docker-compose.yml`
18. Create `.env.example`
19. Create `tests/conftest.py` — async test client, test DB, fixtures
20. Create `tests/integration/test_auth_api.py` — full auth flow coverage
21. Create `tests/unit/test_security.py` — JWT and bcrypt tests
22. Run all tests — must pass at 85%+ coverage

**Phase 1 done when**: `docker-compose up` starts all services, `/health` returns `{"status":"ok"}`, register + login + refresh + logout all work, all tests pass.

---

### PHASE 2 — File Upload & Resume Storage

Tasks in order:
1. Create `backend/app/utils/file_utils.py` — magic byte validation, S3 upload/download, presigned URL generation
2. Create `backend/app/models/resume.py` (already in schema — implement fully)
3. Create `backend/app/schemas/resume.py`
4. Create `backend/app/api/v1/resumes.py` — upload, list, get, delete endpoints
5. Create `backend/app/services/resume_service.py`
6. Create `backend/app/models/job_description.py`
7. Create `backend/app/schemas/job.py`
8. Create `backend/app/api/v1/jobs.py` — save, list, get endpoints
9. Create `backend/app/services/resume_service.py` (JD methods)
10. Write Alembic migration for resumes + job_descriptions tables
11. Create `tests/integration/test_resume_api.py`

---

### PHASE 3 — ML Pipeline

Tasks in order:
1. Create `backend/app/ml/section_parser.py` — pdfplumber + pytesseract + DOCX + magic byte check
2. Create `backend/app/ml/skill_graph.py` — SKILL_ALIASES + SKILL_IMPLIES dicts
3. Create `backend/app/ml/keyword_extractor.py` — hard skills + soft skills + spaCy + alias resolution
4. Create `backend/app/ml/bert_encoder.py` — singleton model, Redis cache, cosine similarity
5. Create `backend/app/ml/tfidf_scorer.py` — TF-IDF cosine similarity
6. Create `backend/app/ml/role_detector.py` — 10 role profiles, keyword scoring, fallback
7. Create `backend/app/ml/llm_scorer.py` — Claude API call, JSON parsing, retry once on failure
8. Create `backend/app/ml/bert_encoder.py` — final score blending (4-score or 3-score)
9. Create `backend/app/workers/celery_app.py` — Celery configuration
10. Create `backend/app/workers/match_tasks.py` — full async pipeline task
11. Create `backend/app/workers/rewrite_tasks.py` — bullet extraction + LLM rewrite task
12. Create `backend/app/models/match_result.py` + `rewrite_session.py`
13. Create `backend/app/api/v1/matches.py` — create, status poll, get result, list
14. Create `backend/app/api/v1/rewriter.py` — create session, get session result
15. Create `backend/app/services/match_service.py`
16. Create `backend/app/services/rewriter_service.py`
17. Write Alembic migration for match_results + rewrite_sessions
18. Create all unit tests: `test_parser.py`, `test_keywords.py`, `test_matcher.py`, `test_role_detector.py`, `test_llm_scorer.py`, `test_rewriter.py`
19. Create `tests/integration/test_match_api.py`

---

### PHASE 4 — Frontend

Tasks in order:
1. Initialize Next.js 14 app with TypeScript, Tailwind, shadcn/ui
2. Create `src/lib/api.ts` — Axios client with JWT interceptor + refresh logic
3. Create `src/types/index.ts` — all shared TypeScript types (User, Resume, Match, etc.)
4. Create authentication pages: `/login`, `/register`
5. Create layout with Navbar and Sidebar
6. Create dashboard page (`/dashboard`)
7. Create resume management (`/dashboard/resumes`)
8. Create match wizard (`/match/new`) — multi-step: pick resume → paste/pick JD → submit
9. Create match result page (`/match/[id]`) — score gauges, keyword badges, section breakdown
10. Create rewriter page (`/rewrite/[id]`) — bullet cards with before/after diff + variant selector
11. Implement `useJobPoller` hook — polls match status every 2s until complete
12. Add loading states, error boundaries, skeleton loaders on all async pages
13. Vitest unit tests for all hooks and key components
14. Playwright E2E: full user journey (register → upload → match → rewrite)

---

### PHASE 5 — Multi-tenancy, Billing & Admin

Tasks in order:
1. Add `tenant_id` row-level filtering to all service layer queries
2. Create `backend/app/api/v1/tenants.py` — admin tenant management
3. Create `backend/app/models/subscription.py`
4. Create `backend/app/services/billing_service.py` — Stripe checkout, portal, webhook
5. Create `backend/app/api/v1/billing.py`
6. Create `backend/app/workers/notification_tasks.py` — SendGrid email tasks
7. Create `backend/app/services/notification_service.py`
8. Add usage enforcement: check match count vs plan limit before dispatching task
9. Create admin pages in frontend (`/admin`) — user management, platform stats
10. Create `tests/integration/test_billing_api.py`
11. Write Alembic migration for subscriptions table
12. Seed script: create default tenant + admin user

---

### PHASE 6 — Observability & Production Hardening

Tasks in order:
1. Add Prometheus metrics endpoint (`/metrics`) with all metrics from Section 10
2. Add Sentry SDK to both backend (Python) and frontend (Next.js)
3. Add Grafana dashboard config files (JSON) for system health + business metrics
4. Add `pip-audit` to CI (already in template above — verify it runs)
5. Add Dependabot configuration (`.github/dependabot.yml`) for Python + npm
6. Full security audit: verify every endpoint has correct auth + role check
7. Load test with Locust: simulate 50 concurrent users running matches, verify p95 < 30s
8. Write final README.md with setup, env vars, architecture overview, contributing guide

---

## Section 16 — What NOT To Do

The agent must never:

- Use `print()` anywhere — use `structlog` logger
- Store secrets in code or comments
- Write `TODO` or `FIXME` comments and leave them — either implement or document as deferred in phase report
- Use `requests` library in async code — use `httpx.AsyncClient`
- Catch bare `except Exception` without logging the error to structlog and Sentry
- Use `SELECT *` queries — always specify columns via SQLAlchemy ORM
- Reinitialize the BERT model more than once (use the singleton in `bert_encoder.py`)
- Call the Claude API synchronously from a FastAPI route handler — always via Celery
- Return HTTP 500 to users without a sanitized error message (never expose stack traces)
- Use `eval()` or `exec()` anywhere
- Store uploaded resume files on local disk in production — S3 only
- Skip tests because "it's obvious" — every function gets a test
- Use `time.sleep()` in async code — use `asyncio.sleep()`
- Truncate or skip any section of this spec — build everything described

