# PixelOps
### A Gamified Chaos Engineering & Observability Dashboard built with FastAPI

PixelOps is an interactive backend resilience simulator that visualizes how production systems behave under failure, latency, retries, and rate limiting.

Designed as both a learning platform and a portfolio project, PixelOps combines chaos engineering concepts with a retro pixel-art dashboard to make backend observability intuitive and engaging.

---

## Features

### Chaos Engineering

- Configurable failure injection
- Adjustable network latency
- Retry mechanism simulation
- Rate limiting
- Real-time chaos configuration

### Observability

- Live metrics dashboard
- Request logging
- Success / Failure analytics
- Average latency tracking
- Status code distribution
- Recent request history

### Replay Engine

- Replay previous simulation sessions
- Adjustable replay speed
- Timeline reconstruction from logs
- Request-by-request playback

### Exporting

- PDF simulation reports
- CSV log export
- Dashboard screenshots

### DevOps

- Docker support
- GitHub Actions CI
- Render deployment
- FastAPI backend

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| Language | Python 3.12 |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Deployment | Render |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Reports | ReportLab |

---

## Dashboard

> Screenshots will be added here.

### Main Dashboard

![Dashboard](docs/dashboard.png)

### Replay Mode

![Replay](docs/replay.png)

### Chaos Controls

![Chaos](docs/chaos.png)

---

## Project Structure

```text
.
├── app/
│   ├── services/
│   ├── main.py
│
├── static/
│   ├── css/
│   ├── js/
│
├── templates/
│
├── reports/
├── data/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Running Locally

Clone the repository

```bash
git clone https://github.com/Taksui/resilient-fastapi-system.git
```

Move into the project

```bash
cd resilient-fastapi-system
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

## Docker

Build

```bash
docker compose build
```

Run

```bash
docker compose up
```

---

## Chaos Controls

PixelOps allows dynamic adjustment of:

- Failure Rate
- Retry Attempts
- Minimum Latency
- Maximum Latency
- Rate Limit

Changes take effect instantly without restarting the application.

---

## Replay System

Every request is persisted into structured logs.

Replay mode reconstructs the simulation timeline, allowing previous traffic sessions to be visualized frame-by-frame.

This demonstrates how system health changes over time under different failure conditions.

---

## CI/CD

GitHub Actions automatically:

- Installs dependencies
- Validates project imports
- Builds the Docker image

on every push and pull request.

---

## Future Improvements

- Authentication
- Multi-user dashboards
- Prometheus integration
- Grafana dashboards
- Kubernetes deployment
- WebSocket live updates
- Distributed service simulation
- AI-powered anomaly detection

---

## Author

**Dave Aashisth T**

Computer Science (AI & ML)

Interested in Backend Engineering, DevOps, Distributed Systems and AI Infrastructure.

---

## License

MIT License