# DevOps Practical Work Assignment

A minimal **Flask** web application containerised with Docker, tested with pytest, and deployed via a GitHub Actions CI pipeline to GitHub Container Registry. Includes Redis as a sidecar service via Docker Compose, and Terraform scripts for provisioning an AWS EC2 instance.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | Flask (Python 3.11) |
| Containerisation | Docker |
| Orchestration | Docker Compose |
| Cache / Queue | Redis |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Infrastructure | Terraform (AWS EC2) |

---

## Project Structure

```
.
├── app/
│   ├── app.py              # Flask app with / and /health routes
│   ├── requirements.txt
│   └── test_app.py         # pytest tests
├── terraform/
│   ├── main.tf             # AWS EC2 + Security Group
│   └── variables.tf        # Instance type and region variables
├── .github/
│   └── workflows/
│       └── ci.yml          # Build, test, push to GHCR
├── Dockerfile
└── docker-compose.yml      # App + Redis stack
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a hello message and running status |
| GET | `/health` | Health check — returns `{"status": "ok"}` |

### Example

```bash
curl http://localhost:8080/
# {"message": "Hello from DevOps!", "status": "running"}

curl http://localhost:8080/health
# {"status": "ok"}
```

---

## Running Locally

### With Docker Compose (App + Redis)

```bash
docker-compose up --build
```

App available at → http://localhost:8080

Redis health is checked automatically before the app container starts.

### With Docker only

```bash
docker build -t devops-app .
docker run -p 8080:5000 devops-app
```

### Without Docker

```bash
pip install -r app/requirements.txt
python app/app.py
```

App runs on port `5000` by default.

---

## Running Tests

```bash
pip install -r app/requirements.txt
pytest app/test_app.py
```

---

## CI Pipeline (GitHub Actions)

Triggers on push and pull requests to `main`.

**Steps:**

1. Checkout code
2. Set up QEMU + Docker Buildx (multi-platform support)
3. Install Python dependencies
4. Run `pytest` tests
5. Log in to GHCR (skipped on PRs)
6. Build and push Docker image to `ghcr.io` (skipped on PRs)

Image is tagged as:
```
ghcr.io/<owner>/devops-practical-work-assignment/devops-app:latest
```

---

## Infrastructure — Terraform (AWS)

The `terraform/` directory provisions a basic AWS EC2 deployment.

**Resources created:**

- `aws_instance` — EC2 instance running the app (default: `t2.micro`, `us-east-1`)
- `aws_security_group` — allows inbound SSH (22) and HTTP (8080), unrestricted outbound

### Usage

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

> **Note:** Requires AWS credentials configured via environment variables or `~/.aws/credentials`.

### Variables

| Variable | Default | Description |
|---|---|---|
| `instance_type` | `t2.micro` | EC2 instance type |
| `region` | `us-east-1` | AWS region |

---

## Docker — Security Practices

- Base image: `python:3.11-slim` (minimal attack surface)
- Dependencies copied first for better layer caching
- App runs as a non-root `appuser` (principle of least privilege)
- `.dockerignore` excludes unnecessary files from the build context
