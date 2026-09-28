# Curriculum Log — 365-Day Python/JavaScript Course

Single source of truth for exactly what's been covered, session by session.
Any future session reads this file first before deciding what comes next —
it does not rely on memory alone.

Format: `Day N, Session S: topic(s) covered`

---

## Backfilled from prior records (Days 1–74)

- Days 1–23: Python fundamentals — variables, loops, functions, OOP, APIs, file handling, Pandas, list comprehensions
- Days 24–31: SQLite + Pandas, Matplotlib/Seaborn (six-chart dashboard), web scraping with BeautifulSoup (User-Agent headers, pagination, pd.read_html(), time.sleep() polite scraping, full multi-page scraper), regular expressions (re.sub/split/compile, named groups, Pandas .str methods), custom exceptions, context managers, logging
- Day 28: Test covering Days 22–28
- Days 32–57: Flask templates and Jinja2 (render_template, passing data to HTML, conditional styling)
- Days 58–62: Tests completed and scored
- Days 61–68: pytest, KM tracking, subscription management, conditionals, dictionary comprehensions, closures, error handling, decorators, generators
- Days 63–70: Subscription management (paid_until, check_trial()), if/elif/else, dictionary/nested function/closure/factory patterns, custom exceptions (SeparakaError, InvalidKMError, TaxiNotFoundError), decorators (parameterized + rate_limit), generators/itertools, advanced pytest (12 passing tests), full OOP depth
- Days 71–74: HTML/CSS (semantic HTML5, Flexbox, responsive/mobile-first), external APIs (requests, python-dotenv, send_sms(), cron architecture), JavaScript DOM/events/form validation, Fetch API with async/await wired to real Flask routes

## Gap — not logged day-by-day

- Days 75–115: covered, but no session-by-session record exists. Known milestones from this window: Day 90 reversed-learning-mode transition (Claude builds, Sechaba reviews/critiques), React introduced via Vite (TaxiCard component, props, useState), around Day 95–96 the course "clicked."
- If specific Day 75–115 topics matter later (e.g. confirming a concept was already taught), ask Sechaba directly rather than assuming — this file is the record going forward, not a reconstruction of the past.

## Logged from Day 116 onward

- Day 116, Session 1: Diagnosed and fixed a 3-layer CI bug in the Separaka E2E test suite — missing UNIQUE constraint on platforms.name, no CI database reset, and a stale seed script (setup_taxi_db.py) silently overriding the test fixture's platform_id for marshall1. This was app/CI debugging work, not a new course concept.
- Day 116, Session 2: Built and integrated a branded animated loading screen (navy background, three horizontal pulsing bars, SEPARAKA wordmark) across taxi_login, taxi_marshall, taxi_dashboard, taxi_driver, taxi_admin_taxis, and taxi_marshalls_admin. Also found and cleaned up a stray duplicate template (taxi_marshalls_admin.html.html) that wasn't wired to any route. Design/product work, not a new course concept.

## Rules for any Claude session working on this course

1. Read this entire file FIRST, before saying anything about what comes
   next. Never guess or estimate from an old roadmap note — this file is
   the only source of truth for what's been covered.

2. Never state a fact about Sechaba's business (clients, payments,
   revenue, deals closed) unless he has said it in THIS conversation.
   Old notes go stale; don't repeat them as if current.

3. Every session — course lesson or app/business work — ends with one
   new line added to this file before the conversation ends. No
   exceptions, done before the final push of that session.

4. A "Day N" label is only used for an actual course lesson (recap →
   numbered lessons → task, per the course structure below). App or
   business work done the same calendar day is logged under that day
   too, but marked "app work" — it never implies a lesson happened if
   one didn't.

5. A new chat opens by reading this file (Sechaba will attach or paste
   it), then gives a recap linking to the last real lesson before
   starting anything new. It never opens by asking Sechaba what comes
   next — that's the teacher's job.

6. Standing priority: the AI passenger-counting camera (YOLO / computer
   vision) is tied to real client demand and takes precedence in
   scheduling over incidental app polish, unless Sechaba says otherwise.

## Course structure (for reference)

Each lesson session opens with a recap linking to prior work, then
2–4 numbered Lessons (concept explanation → one full code block →
numbered task), closing with a business-use-case lesson. Depth matches
university-level rigor. Two-line sessions are unacceptable.
