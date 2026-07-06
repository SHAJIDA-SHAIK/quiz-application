# Retro Quiz — PRD

## Problem
Build a quiz website (originally a CLI project) with User System (name + welcome), Main Menu (Start Quiz / Leaderboard / Exit), 20+ MCQs across Python/DBMS/OS/Aptitude, difficulties Easy/Medium/Hard, shuffle, input validation, score tracking, show correct answers for wrong responses, per-question timer, saved scores, leaderboard top 5, performance stats, colorful terminal output, error handling.

## User choices
- MongoDB persistence
- JWT signup/login accounts
- Retro/terminal-inspired aesthetic (green-on-black CRT vibe)
- 20s timer per question

## Implemented (v1 — Feb 2026)
- FastAPI backend with JWT httpOnly-cookie auth (register/login/logout/me)
- 44-question bank (11 per category × 4 categories, mixed difficulties)
- Endpoints: /api/quiz/{categories,start,submit,leaderboard,stats}
- React frontend with 8 routes: /login /register / /setup /quiz /results /leaderboard /stats
- Retro-terminal UI: JetBrains Mono, scanlines, CRT flicker, glowing green text, ASCII progress bar
- 20s per-question countdown (yellow at ≤10s, red flash at ≤5s), auto-advance on timeout
- Full answer review: correct answer highlighted green, wrong choice highlighted red
- Global leaderboard with per-category filter
- Personal stats (games, best score, avg accuracy, per-category breakdown, recent sessions)

## Backlog (P1/P2)
- Expand question bank to 20/category (need +9/cat)
- Difficulty mixing within a single quiz
- Time-taken bonus scoring
- Personal high-score badges on leaderboard
- Password reset / forgot password flow
- Question categories authored by admins (admin dashboard)

## Next actions
- (P1) Add more questions per category
- (P1) Add personal-best highlight on leaderboard
