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
- Day 116, Session 2: *(pending — computer vision / YOLO track begins here, per the Day 100–120 roadmap)*
