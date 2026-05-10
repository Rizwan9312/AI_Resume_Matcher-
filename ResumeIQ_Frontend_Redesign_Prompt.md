# ResumeIQ — Enterprise Frontend Redesign Prompt
### Antigravity Design System · Complete Page-by-Page Specification

---

## 🔒 CRITICAL CONSTRAINT — READ FIRST

> **DO NOT modify any backend files, API routes, environment variables, database models, Celery tasks, ML pipeline, or any file outside the `frontend/src/` directory. Only touch frontend presentation layer files: `.tsx`, `.css`, `.ts` (types/utils only), and `tailwind.config.ts`. All existing API contracts, data shapes, and business logic remain 100% unchanged.**

---

## 🎨 Design System & Aesthetic Direction

Apply a unified **"Antigravity"** design language across all pages. This is a dark-mode enterprise aesthetic inspired by zero-gravity environments — deep space blacks, luminous accent glows, floating card surfaces, and physics-defying layouts that feel weightless yet authoritative.

---

### Color Tokens

Establish these in `globals.css` and `tailwind.config.ts`:

| Token | Value | Usage |
|---|---|---|
| Background | `#050508` | Page base (near-void black) |
| Surface | `#0D0D14` | Elevated card surface |
| Surface-2 | `#13131E` | Nested surface |
| Border | `rgba(255,255,255,0.06)` | All card/container borders |
| Primary Accent | `#6C63FF` | Electric indigo — buttons, active states |
| Secondary Accent | `#00D4FF` | Cyan glow — highlights, gradients |
| Success | `#00FF88` | Neon mint — matched keywords, high scores |
| Warning | `#FFB800` | Amber — mid-range scores |
| Danger | `#FF4D6D` | Coral red — missing keywords, low scores |
| Text Primary | `#F0F0FF` | Main readable text |
| Text Secondary | `#8888AA` | Subtitles, labels |
| Text Muted | `#444466` | Placeholders, meta info |

---

### Typography

| Role | Font | Source |
|---|---|---|
| Display / Hero | `Syne` (weights 400, 700, 800) | `next/font/google` |
| Body | `DM Sans` (weights 400, 500) | `next/font/google` |
| Monospace / Data | `JetBrains Mono` | Already in project — keep |

Install via `next/font/google` in `src/app/layout.tsx` and expose as CSS variables `--font-display` and `--font-body`.

---

### Signature Effects

- **Glass cards:** `backdrop-filter: blur(20px)` + `border: 1px solid rgba(255,255,255,0.06)` — surfaces float in the void
- **Floating orbs:** Large blurred `position: fixed` radial gradient blobs in the background (`pointer-events: none`, `z-index: 0`) — creates depth layers
- **Glow on hover:** `box-shadow: 0 0 20px rgba(108,99,255,0.4)` on all interactive elements
- **Lift on hover:** `transform: translateY(-2px)` on cards
- **Transitions:** `transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)` universally applied
- **Section labels:** Small muted uppercase monospace labels like `01 / FEATURES` for editorial structure

---

### Button Variants

| Variant | Style |
|---|---|
| `primary` | `background: linear-gradient(135deg, #6C63FF, #00D4FF)`, white text, glow shadow on hover |
| `ghost` | Transparent, `border: 1px solid rgba(255,255,255,0.12)`, white text, slight fill on hover |
| `danger` | `background: #FF4D6D`, white text |

---

## 🧩 Shared Components to Create

Create these reusable components before building any page.

### `src/components/FloatingOrbs.tsx`
Renders 2–3 `position: fixed` blurred div orbs with a slow CSS `@keyframes float` animation (6-second up-down loop, 20px range, low opacity). Use on landing page and auth pages only — not on dashboard.

### `src/components/GlassCard.tsx`
A reusable `div` wrapper with the standard glass surface styles, hover lift effect, and border. Accept `className` and `children` as props.

### `src/components/ScoreRing.tsx`
SVG-based circular progress ring. Props: `score: number`, `size?: number`, `strokeWidth?: number`. Animates from 0 to `score` on mount using CSS transition on `stroke-dashoffset`. Color is dynamic: green if ≥ 80, yellow if 60–79, red if < 60.

### `src/components/Button.tsx`
Unified button component with `variant: 'primary' | 'ghost' | 'danger'`, `size: 'sm' | 'md' | 'lg'`, and standard `onClick` / `type` props.

---

## 📄 Page 1 — Landing Page

**File:** `src/app/page.tsx` + `src/app/globals.css`
Keep all existing Next.js routing and link `href` values unchanged.

---

### 1.1 Navbar

- Fixed top, `backdrop-filter: blur(16px)`, `background: rgba(5,5,8,0.8)`
- **Left:** `ResumeIQ` logo in Syne bold with a small glowing dot (accent color) after the "Q"
- **Right:** `Sign In` (ghost button) → `/login` and `Get Started` (primary button with glow) → `/register`
- On scroll past 80px: a thin 1px bottom border fades in via CSS transition on the navbar container

---

### 1.2 Hero Section

- Full viewport height (`min-h-screen`), content centered vertically and horizontally
- **Background:** 3 `<FloatingOrbs />` — one large indigo (`#6C63FF`, 15% opacity, 600px blur), one cyan (`#00D4FF`, 10% opacity, 400px blur), one bottom-right. All animated with slow float keyframe
- **Badge:** Small pill above headline — `✦ AI-Powered Resume Intelligence` — bordered, glowing, uppercase tiny text
- **Headline** (Syne, 72px desktop / 40px mobile):
  ```
  Match Smarter.
  Land Faster.          ← "Faster" in var(--accent-primary) color
  ```
- **Subheadline** (DM Sans, 20px, muted): *"ResumeIQ analyzes your resume against any job description using BERT, TF-IDF, and LLM scoring — then rewrites it to get you hired."*
- **CTA Buttons:** `Analyze My Resume →` (primary, large) and `See How It Works` (ghost)
- **Trust bar:** Horizontal pill container with 3 stats separated by thin vertical dividers:
  - `10,000+ Resumes Analyzed`
  - `94% Match Accuracy`
  - `Free to Start`

---

### 1.3 How It Works Section

- Section label: `01 / HOW IT WORKS` (small, muted, monospace)
- Headline: *"Three Steps to Your Next Job"*
- Three numbered glass cards in a horizontal grid (stack on mobile):

| Step | Title | Description |
|---|---|---|
| `01` | Upload Resume | Upload your PDF or DOCX resume |
| `02` | AI Scoring | BERT + TF-IDF + Keyword + LLM analysis |
| `03` | Auto-Rewrite | AI rewrites your resume to match the job |

- Each card has a glowing top border (1px gradient from accent to transparent)
- The step number (80px Syne, opacity 0.08) displays behind the icon as a large decorative watermark

---

### 1.4 Features Section

- Section label: `02 / FEATURES`
- Headline: *"Enterprise-Grade Analysis"*
- Asymmetric bento-grid layout:
  - **Large card** (spans 2 columns): "Multi-Dimensional Scoring" — decorative mock score UI with 4 glowing progress bars (BERT, TF-IDF, Keyword, LLM) — purely cosmetic HTML/CSS, no real data
  - **3 smaller cards:** Role-Aware Weighting, Keyword Gap Analysis, One-Click Rewrite
- All cards: glass surface + hover lift

---

### 1.5 Score Preview Section

- Section label: `03 / RESULTS`
- Headline: *"See What Your Score Looks Like"*
- One large centered **mock result card** showing:
  - A fake `82 / 100` score with a `<ScoreRing />` SVG (animates on scroll via Intersection Observer)
  - 4 metric breakdown bars
  - Sample matched keywords (green tags) and missing keywords (red tags)
- Below the card: 2–3 short user testimonial quotes in minimal glass cards (software engineer, marketing manager, data scientist personas)

---

### 1.6 CTA Banner

- Full-width dark panel with a radial glow at center
- Headline: *"Ready to Outmatch the Competition?"*
- Single large primary CTA: `Start for Free — No Credit Card` → `/register`

---

### 1.7 Footer

- Minimal three-column layout: Logo (left) | Nav links — `Features`, `Sign In`, `Register` (center) | Copyright (right)
- `border-top: 1px solid rgba(255,255,255,0.06)`

---

## 📄 Page 2 — Sign In Page

**File:** `src/app/(auth)/login/page.tsx`
Do not change form submission logic, API call, or token storage. Visual redesign only.

---

### Layout: Full-Screen Split Panel

- **Left panel (55% width, hidden on mobile):** Visual side
- **Right panel (45% width, full width on mobile):** Form side

---

### Right Panel — Form

- Background: `#050508` with `<FloatingOrbs />`
- Top-left: `ResumeIQ` logo linking back to `/`
- Centered vertically:
  - Label: `WELCOME BACK` (small, muted, uppercase, monospace)
  - Headline (Syne, 36px): *"Sign in to your workspace"*
  - Subtext (muted): *"Continue your job search journey."*
  - **Email field** — dark surface input: `background: #0D0D14`, `border: 1px solid rgba(255,255,255,0.08)`, focus: `border-color: #6C63FF` + `box-shadow: 0 0 0 3px rgba(108,99,255,0.2)`
  - **Password field** — same styling + show/hide toggle icon
  - **"Forgot password?"** — right-aligned, muted, small
  - **Submit button:** Full-width, primary, large — `Sign In →`
  - Divider: horizontal line with `or` centered
  - **Footer link:** `Don't have an account? [Create one →]` → `/register`

> Keep all existing `onChange`, `onSubmit`, state variables, and error display. Only wrap them in the new JSX markup.

---

### Left Panel — Visual

- Background: `#0D0D14`
- Large centered decorative element: abstract SVG/CSS illustration of a floating resume card with a glowing score ring (purely decorative, not interactive)
- Below illustration: 3 benefit statements cycling every 3 seconds via CSS animation:
  - *"BERT + TF-IDF scoring"*
  - *"Role-aware weighting"*
  - *"One-click AI rewrite"*
- Bottom: single user testimonial quote in a small glass card

---

## 📄 Page 3 — Register Page

**File:** `src/app/(auth)/register/page.tsx`
Do not change registration logic, API calls, field validation, or error handling. Visual redesign only.

---

### Layout: Full-Screen Centered (Single Column)

- Background: `#050508` with 2 `<FloatingOrbs />`
- Top-center: `ResumeIQ` logo
- **Decorative progress indicator:** `Step 1 of 3` pill at top (purely decorative — communicates enterprise onboarding quality even if single-step)
- **Card container:** `max-width: 480px`, centered, glass surface, `border-radius: 24px`, `padding: 48px`

---

### Inside Card

- Label: `CREATE ACCOUNT` (small, muted, uppercase, monospace)
- Headline (Syne, 28px): *"Start matching smarter"*
- **Form fields** — all restyled with dark surface + accent focus ring:
  - Full Name
  - Email
  - Password + strength indicator (4-segment bar below, fills based on length/complexity — pure CSS/JS, no backend)
  - Confirm Password
  - Role selector → replace `<select>` with 3 pill-toggle buttons: `Job Seeker` / `Recruiter` / `Admin` — keep existing state and `onChange` logic, only replace the JSX wrapper
- **Submit button:** Full-width, primary — `Create Free Account →`
- **Footer link:** `Already have an account? [Sign In]` → `/login`
- **Disclaimer:** `By continuing, you agree to our Terms of Service` (tiny, muted, centered)

---

## 📄 Page 4 — Dashboard

**File:** `src/app/dashboard/page.tsx`
Do not change data fetching, API calls, React Query hooks, or navigation logic.

---

### Layout: Sidebar + Main Content

#### Sidebar (fixed left, 240px wide)

- Background: `#0D0D14`, `border-right: 1px solid rgba(255,255,255,0.06)`
- Top: `ResumeIQ` logo with glow dot
- Nav items using existing `lucide-react` icons:

| Icon | Label | Route |
|---|---|---|
| LayoutDashboard | Dashboard | `/dashboard` |
| FileText | Resumes | `/dashboard/resumes` |
| BarChart2 | Matches | `/dashboard/matches` |
| Wand2 | Rewrite | — |
| Settings | Settings | — |

- **Active item:** 3px left accent border (`#6C63FF`) + slightly brighter background
- **Bottom:** User avatar placeholder + name + `Sign Out` button
- **Mobile:** Collapses to icon-only with hamburger toggle

---

#### Main Content Area

- Background: `#050508`
- **Header:** `Good morning, [Name]` (Syne, 28px) + current date (muted, right-aligned)
- **Stats row:** 4 glass cards in a grid:
  - Resumes Uploaded
  - Matches Run
  - Average Score
  - Rewrites Done
  - Each: large number (JetBrains Mono) + label + small icon
- **Recent Matches table:** Glass surface card, columns:
  - Resume Name | Job Title | Score (colored by threshold) | Status badge | Date | Actions
  - Score color: green ≥ 80, yellow 60–79, red < 60
- **Quick Actions:** Two large glass CTA cards — `Upload New Resume` and `Start New Match` — with icons and glow hover

---

## 📄 Page 5 — New Match Page

**File:** `src/app/match/new/page.tsx`
Do not change form submission logic or API calls.

---

### Layout: Full-Width Focused Task UI (No Sidebar)

- Back link to `/dashboard` at top-left
- Headline (Syne): *"New Match Analysis"*
- **Two-column form** (stack on mobile):
  - **Left column:** Resume selector — stylized card-list of the user's uploaded resumes. Each resume shown as a small glass card with filename, upload date, and a radio-select indicator
  - **Right column:** Job Description — large `<textarea>` (dark surface, JetBrains Mono, `min-height: 200px`) with character count below
- **File upload zone** (alternative to resume selector): Dashed animated border, upload icon, `Drag your resume here or click to browse`
- **Scoring Method display:** 4 read-only pill badges — `BERT`, `TF-IDF`, `Keyword Match`, `LLM Judge` — with lock icons (purely decorative, communicates enterprise credibility)
- **Submit button:** Full-width, primary, large — `Run AI Analysis →`
- **Loading state** (after submission): Replace button with animated step counter:
  ```
  ⟳  Parsing resume...
  ⟳  Extracting keywords...
  ⟳  Running BERT...
  ⟳  LLM scoring...
  ```
  Each step cycles in with a spinner and progress indicator.

---

## 📄 Page 6 — Match Result Page

**File:** `src/app/match/[id]/page.tsx`
Do not change data fetching, polling logic, or the rewrite trigger API call.

---

### Layout

- Header: back button + *"Match Analysis Results"* (Syne)
- **Hero score card:** Large glass surface, centered:
  - `<ScoreRing />` SVG that animates on mount
  - Score number (JetBrains Mono, 64px) in the ring center
  - Label below: `Overall Match Score`
- **4 metric cards** in a row below the ring — each a small glass card:
  - BERT Score | TF-IDF Score | Keyword Score | LLM Score
  - Each: horizontal progress bar + value (JetBrains Mono) + label
- **Role detected badge:** Small pill — `Detected Role: [Engineering]` with icon
- **Two-column keyword section:**
  - Left: Matched Keywords — green tags with `✓` icons
  - Right: Missing Keywords — red tags with `✗` icons
- **AI Feedback card:** Glass surface, `AI Feedback` heading, `feedback_text` content
- **LLM Verdict:** Collapsible section (click to expand), renders raw verdict JSON in a styled code block
- **Rewrite CTA banner** (conditional — only shown if score < 80):
  ```
  Your score is below 80. Let AI rewrite your resume.
  [ Rewrite My Resume → ]     ← links to /rewrite/[match_id]
  ```
  Large glowing banner with the primary button.

---

## 📄 Page 7 — Rewrite Page

**File:** `src/app/rewrite/[match_id]/page.tsx`
Do not change polling logic, API calls, or download logic.

---

### Three-State UI (map to `status` from API)

#### State 1: `pending` / `processing`

- Full-screen centered loading state
- Animated pulsing orb (CSS keyframe)
- Step labels cycling:
  - *"Analyzing job description..."*
  - *"Extracting key requirements..."*
  - *"Rewriting experience section..."*
  - *"Optimizing for ATS..."*
- Indeterminate progress bar below steps

---

#### State 2: `complete`

- **Two-column layout:**
  - Left: Original resume sections (collapsible glass cards)
  - Right: Rewritten sections (highlighted with green background on new/changed text)
- Each rewritten section is a glass card with section header (`Experience`, `Skills`, etc.) + content + small `AI-generated` badge
- **Download button** (full-width, primary, below both columns): `Download Optimized Resume (.txt)` with download icon — keep existing download logic

---

#### State 3: `failed`

- Error state glass card, centered
- Error message + `Retry` button (ghost variant)

---

## ⚙️ Global Implementation Rules

### Package Constraints
Do not install any new npm packages. Use only what is already in `package.json`:
- Next.js 14, React 18, TailwindCSS 3.4
- `lucide-react` — icons
- `Axios` — HTTP
- `@tanstack/react-query` v5 — data fetching
- `next/font/google` — for Syne and DM Sans (no extra install needed)

---

### Tailwind Config Additions (`tailwind.config.ts`)
Add to the existing config — do not remove existing tokens:

```ts
extend: {
  colors: {
    bg: '#050508',
    surface: '#0D0D14',
    'surface-2': '#13131E',
    accent: '#6C63FF',
    cyan: '#00D4FF',
    success: '#00FF88',
    warning: '#FFB800',
    danger: '#FF4D6D',
  },
  fontFamily: {
    syne: ['var(--font-syne)', 'sans-serif'],
    'dm-sans': ['var(--font-dm-sans)', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  boxShadow: {
    glow: '0 0 20px rgba(108,99,255,0.4)',
    'glow-cyan': '0 0 20px rgba(0,212,255,0.3)',
    'glow-success': '0 0 20px rgba(0,255,136,0.3)',
  },
}
```

---

### TypeScript Rules
- Do not break any existing TypeScript types
- New component props must be optional with sensible defaults
- Do not alter any existing interface or type in `src/types/`

---

### Accessibility Requirements
- All interactive elements: proper `aria-label`
- Focus rings: styled with accent color (`outline: 2px solid #6C63FF`), not browser default
- Full keyboard navigability on all forms and nav items

---

### Responsive Breakpoints
Every page must be fully responsive using Tailwind prefixes:

| Breakpoint | Behavior |
|---|---|
| `< md` (mobile) | Sidebar collapses, split layouts stack, hero text scales to 40px |
| `md:` (tablet) | Partial sidebar (icon-only), 1-column forms |
| `lg:` (desktop) | Full sidebar, split panels, bento grids |

---

### Execution Order

Work through pages in this exact sequence:

1. `globals.css` — design tokens, keyframes, base styles
2. `tailwind.config.ts` — color/font/shadow extensions
3. `layout.tsx` — font installation, CSS variable binding
4. Shared components — `FloatingOrbs`, `GlassCard`, `ScoreRing`, `Button`
5. **Landing page** — `src/app/page.tsx`
6. **Sign In page** — `src/app/(auth)/login/page.tsx`
7. **Register page** — `src/app/(auth)/register/page.tsx`
8. **Dashboard** — `src/app/dashboard/page.tsx`
9. **New Match** — `src/app/match/new/page.tsx`
10. **Match Result** — `src/app/match/[id]/page.tsx`
11. **Rewrite** — `src/app/rewrite/[match_id]/page.tsx`

---

*ResumeIQ · Antigravity Design System · Frontend Specification v1.0*
