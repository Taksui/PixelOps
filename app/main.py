from fastapi import FastAPI, Request, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.services.export_service import generate_pdf
from app.services.replay_service import replay

import os
import json
import time

from app.services.logger import log_request
from app.services.metrics import metrics
from app.services.chaos_engine import chaos
from app.services.chaos_config import chaos_config
from app.services.rate_limiter import rate_limiter

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "logs.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
def startup():

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE, "w") as f:
            json.dump([], f)


# ============================================================
# DATA ENDPOINT
# ============================================================

@app.get("/data")
def get_data(request: Request):

    start = time.time()

    client_ip = request.client.host

    # Session ID at the moment request started
    request_session = metrics.session_id

    # --------------------------------------------------------
    # Rate Limiting
    # --------------------------------------------------------

    if not rate_limiter.allow_request(
        client_ip,
        chaos_config.rate_limit
    ):

        latency = time.time() - start

        response = {
            "error": "Rate limit exceeded"
        }

        # Ignore stale requests after reset
        if request_session == metrics.session_id:

            metrics.record_rate_limit()

            log_request(
                endpoint="/data",
                client_ip=client_ip,
                status="RATE_LIMITED",
                latency=latency,
                response=response,
                attempts=1
            )

        return response

    # --------------------------------------------------------
    # Latency
    # --------------------------------------------------------

    chaos.inject_latency()

    # --------------------------------------------------------
    # Risky Operation
    # --------------------------------------------------------

    def risky_operation():

        if chaos.should_fail():
            raise Exception("Simulated Failure")

        return {
            "message": "Success"
        }

    # --------------------------------------------------------
    # Retry
    # --------------------------------------------------------

    try:

        result, attempts = chaos.retry(
            risky_operation
        )

        latency = time.time() - start

        # Ignore stale requests after reset
        if request_session == metrics.session_id:

            metrics.record_success(
                latency,
                attempts
            )

            log_request(
                endpoint="/data",
                client_ip=client_ip,
                status="SUCCESS",
                latency=latency,
                response=result,
                attempts=attempts
            )

        return result

    except Exception:

        latency = time.time() - start

        response = {
            "error": "Failed after retries"
        }

        # Ignore stale requests after reset
        if request_session == metrics.session_id:

            metrics.record_failure(
                latency,
                chaos_config.retry_attempts
            )

            log_request(
                endpoint="/data",
                client_ip=client_ip,
                status="FAILED",
                latency=latency,
                response=response,
                attempts=chaos_config.retry_attempts
            )

        return response


# ============================================================
# Metrics
# ============================================================

@app.get("/metrics")
def get_metrics():

    return {

        **metrics.to_dict(),

        "failure_rate_setting":
            chaos_config.failure_rate,

        "rate_limit":
            chaos_config.rate_limit,

        "latency_range": [

            chaos_config.min_latency,

            chaos_config.max_latency

        ],

        "retry_limit":
            chaos_config.retry_attempts
    }


# ============================================================
# Replay
# ============================================================

@app.get("/replay")
def replay_logs():

    try:

        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

    except Exception:

        logs = []

    return {

        "total_logs": len(logs),

        "recent_logs": logs[-10:]
    }


# ============================================================
# Dashboard API
# ============================================================

@app.get("/dashboard-data")
def dashboard_data():

    return {

        "metrics": metrics.to_dict(),

        "recent_logs": replay_logs()["recent_logs"]

    }


# ============================================================
# Chaos Configuration
# ============================================================

@app.get("/chaos/current")
def current_chaos():

    return chaos_config.to_dict()


@app.post("/chaos/update")
def update_chaos(settings: dict = Body(...)):

    chaos_config.update(settings)

    return {

        "message": "Chaos updated.",

        "config": chaos_config.to_dict()

    }


# ============================================================
# Reset Simulation
# ============================================================

@app.post("/reset")
def reset():

    metrics.reset()

    rate_limiter.clients.clear()

    with open(LOG_FILE, "w") as f:

        json.dump([], f)

    return {

        "message": "Simulator reset."

    }

# ============================================================
# Replay API
# ============================================================

@app.get("/replay/start")
def replay_start():

    frames = replay.build_frames()

    return {

        "total_frames": len(frames),

        "frames": frames

    }


@app.get("/replay/info")
def replay_info():

    frames = replay.build_frames()

    if not frames:

        return {

            "available": False,

            "total_frames": 0

        }

    return {

        "available": True,

        "total_frames": len(frames),

        "first_frame": frames[0],

        "last_frame": frames[-1]

    }

# ============================================================
# Dashboard
# ============================================================

@app.get("/")
@app.get("/dashboard")
def dashboard():

    return FileResponse(
        os.path.join(
            "templates",
            "dashboard.html"
        )
    )

# ============================================================
# Export Report
# ============================================================

@app.get("/export/report")
def export_report():

    try:

        with open(LOG_FILE, "r") as f:

            logs = json.load(f)

    except Exception:

        logs = []

    pdf_path, csv_path = generate_pdf(

        metrics.to_dict(),

        chaos_config.to_dict(),

        logs

    )

    return FileResponse(

        path=pdf_path,

        filename=os.path.basename(pdf_path),

        media_type="application/pdf"

    )