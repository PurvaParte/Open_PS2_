# EvidentAI Backend

FastAPI backend for recording session events, replaying timelines, and generating explainable integrity-review signals. Signals are indicators for human review, not proof of misconduct.

## Requirements
- Python 3.10+ (recommended: Python 3.11 or 3.12)

## Setup
Run these commands from the `backend` directory.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows; on macOS/Linux use: cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation and `http://127.0.0.1:8000/health` for health status. The default database is SQLite at `evidentai.db` relative to the working directory. Set `DATABASE_URL` in `.env` to use another SQLAlchemy-supported database.

## API
- `GET /` — service info
- `GET /health` — database health check
- `POST /sessions` — create a session (`{"student_id":"student-1"}`)
- `GET /sessions` — list sessions (supports `skip` and `limit`)
- `GET /sessions/{id}` — session details
- `POST /sessions/{id}/end` — mark a session ended
- `POST /record_event` — record an event (`session_id`, millisecond `timestamp`, `event_type`, `data`)
- `GET /replay/{id}` — ordered event timeline
- `GET /analyze/{id}` — run integrity rules without saving results
- `POST /analyze/{id}/save` — replace and save the current analysis signals
- `GET /signals/{id}` — retrieve saved signals

Allowed event types: `insert`, `delete`, `paste`, `run`, `focus`, `blur`, `submit`, `other`. `data` can be text or a JSON object/list (which is serialized to JSON text).

## Notes
- The original `/record_event`, `/replay/{session_id}`, and `/analyze/{session_id}` routes remain available.
- SQLite foreign keys are enabled. Existing databases are retained; `create_all` creates missing tables but does not migrate existing schemas. Use a migration tool such as Alembic before changing production schemas.
- Integrity thresholds can be configured via environment variables listed in `.env.example`.
