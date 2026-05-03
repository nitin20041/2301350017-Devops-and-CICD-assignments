# Docker Infrastructure Assignment 2 — StackForge To-Do API

A production-grade To-Do REST API built with **FastAPI** and **SQLite**, containerised with Docker and deployed with a full CI/CD pipeline to GitHub Container Registry. Includes structured JSON logging, Prometheus metrics, and a multi-stage Docker build.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Database | SQLite (swappable via `DATABASE_URL`) |
| ORM | SQLAlchemy |
| Logging | python-json-logger (structured JSON) |
| Metrics | Prometheus (`prometheus_client`) |
| Containerisation | Docker (multi-stage build) |
| Monitoring | Prometheus |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |

---

## Project Structure

```
.
├── src/
│   ├── main.py               # FastAPI app — routes, DB models, middleware
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
├── infra/
│   └── prometheus.yml        # Prometheus scrape config
├── .github/
│   └── workflows/
│       ├── ci.yml            # Lint, test, Docker build verification
│       └── cd.yml            # Push image to GHCR on merge to main
├── Dockerfile                # Multi-stage build
├── docker-compose.yml        # API + Prometheus stack
├── render.yaml               # Render.com deployment config
└── ANSWERS.md                # Written theory answers
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| GET | `/metrics` | Prometheus metrics scrape endpoint |
| GET | `/todos` | List all to-do items |
| POST | `/todos` | Create a new to-do item |
| PUT | `/todos/{id}` | Update a to-do item |
| DELETE | `/todos/{id}` | Delete a to-do item |

### Example

```bash
# Create a to-do
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'

# List all to-dos
curl http://localhost:3000/todos

# Mark as done
curl -X PUT http://localhost:3000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

---

## Running Locally

### With Docker Compose (API + Prometheus)

```bash
docker-compose up --build
```

- API → http://localhost:3000
- Prometheus → http://localhost:9090

### With Docker only

```bash
docker build -t todo-api .
docker run -p 3000:3000 todo-api
```

### Without Docker

```bash
pip install -r src/requirements.txt
cd src
uvicorn main:app --host 0.0.0.0 --port 3000
```

---

## Docker — Multi-Stage Build

The Dockerfile uses a two-stage build to keep the final image lean:

- **Builder stage** — installs `build-essential` and `libpq-dev`, compiles all Python dependencies.
- **Runtime stage** — copies only the installed packages and app source. Runs as a non-root `appuser` for security.

A `HEALTHCHECK` is baked in, polling `/health` every 30 seconds.

---

## CI/CD Pipeline

### CI (`ci.yml`) — triggers on push/PR to `main`

1. Lints with `flake8` (hard errors + style warnings)
2. Runs unit tests via `pytest`
3. Builds the Docker image and verifies it starts and passes `/health`

### CD (`cd.yml`) — triggers after CI succeeds on `main`

1. Logs in to GHCR using `GITHUB_TOKEN`
2. Tags the image as `latest` and with the short commit SHA
3. Builds and pushes to `ghcr.io/<your-repo>`
4. Outputs the image digest to the workflow summary

---

## Observability

Structured JSON logs are emitted for every request, including method, path, status code, and latency.

Prometheus metrics exposed at `/metrics`:

- `http_requests_total` — counter by method, endpoint, status
- `http_request_duration_seconds` — histogram of request latency

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/todos.db` | SQLAlchemy DB connection string |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`) |
