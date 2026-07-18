# Retro Quiz — PRD

## Problem
Retro/terminal-themed quiz website. CS/programming categories with timed MCQs, JWT auth, leaderboard, admin dashboard, AI-generated quizzes, certificates, and Docker deployment.

## User choices
- MongoDB persistence
- JWT (httpOnly cookies, SameSite=None, Secure)
- Retro/terminal aesthetic (green-on-black CRT + scanlines)
- 20s timer per question
- AI: Gemini 3 Flash via Emergent Universal Key
- Email verification & password reset: DEV MODE (log/return dev links; no external email provider)
- Certificate format: PDF (reportlab)
- Negative marking: -5 per wrong answer (toggleable in Setup)
- Dark-only theme (no light mode toggle)
- Docker: `docker-compose.yml` + backend/frontend Dockerfiles included

## Implemented
### Iteration 1 (Feb 2026)
- JWT auth (register/login/logout/me) via httpOnly cookies
- 44-question bank (Python/DBMS/OS/Aptitude × Easy/Medium/Hard)
- Quiz flow: setup → timed play → results → review → leaderboard/stats
- Full retro-terminal UI: JetBrains Mono, scanlines, glowing text, ASCII progress bar
- Mobile responsive layouts

### Iteration 2 (Jul 2026)
- Question bank expanded to **80 questions (20/category)**
- **Admin account** auto-seeded on startup (admin@quiz.sys)
- **Admin console** at `/admin`: analytics (users/verified/games/questions/avg accuracy, per-category bars, top-5 players), manual question CRUD, AI question generator
- **AI-generated quizzes** — Gemini 3 Flash produces MCQs on any topic; admin reviews and saves to bank
- **Password reset flow** — forgot-password + reset-password with dev links (returned/shown on-screen)
- **Email verification** — dev links shown on-screen; resend endpoint; yellow verify banner on Home
- **Negative marking** — toggle in Setup, -5 per wrong (skipped not penalized)
- **Certificate PDF** — reportlab retro-theme certificate download from Results
- **Pass/fail badge** — accuracy ≥ 70% marks the run passed
- **Leaderboard highlight** — current user's rows outlined with "← YOU" badge
- **Analytics dashboard** — admin-only, per-category and top-player breakdowns
- **Docker deployment** — `Dockerfile` (backend), `Dockerfile` + `nginx.conf` (frontend), `docker-compose.yml` at repo root, `DOCKER.md` instructions

## Backlog (P2)
- Actual email delivery via Resend/SendGrid (currently dev links only)
- Personal high-score badge per user on their history
- Question tags / search in admin bank
- Shareable result cards (PNG for social)
- OAuth (Google) login option

## Next actions
- (P2) Wire real email provider when user supplies keys
- (P2) Add shareable retro result card (PNG export via html-to-canvas or backend PIL)
