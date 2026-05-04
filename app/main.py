from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import random
import time
import json
from datetime import datetime
import os

app = FastAPI()

# ------------------ CONFIG ------------------
FAILURE_RATE = 0.3
DELAY_RANGE = (0.2, 1.5)
RATE_LIMIT = 5

# ------------------ GLOBALS ------------------
request_count = 0
failure_count = 0
user_requests = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "logs.json")

# Ensure data folder exists
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ------------------ RETRY LOGIC ------------------
def retry(func, retries=3, base_delay=0.5):
    for attempt in range(retries):
        try:
            return func()
        except Exception:
            if attempt == retries - 1:
                raise
            # 🔥 Exponential backoff
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)

# ------------------ LOGGER ------------------
def log_request(endpoint, data):
    log_entry = {
        "timestamp": str(datetime.now()),
        "endpoint": endpoint,
        "data": data
    }

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

# ------------------ MAIN ENDPOINT ------------------
@app.get("/data")
def get_data(request: Request):
    global request_count, failure_count

    request_count += 1
    start_time = time.time()

    client_ip = request.client.host

    # Rate limiting
    user_requests[client_ip] = user_requests.get(client_ip, 0) + 1
    if user_requests[client_ip] > RATE_LIMIT:
        response_time = time.time() - start_time
        error = {"error": "Rate limit exceeded"}

        log_request("/data", {
            "response": error,
            "response_time": response_time
        })

        return error

    # Simulated latency
    delay = random.uniform(*DELAY_RANGE)
    time.sleep(delay)

    # Simulated failure
    def risky_operation():
        if random.random() < FAILURE_RATE:
            raise Exception("Simulated API failure")
        return {"message": "Success"}

    try:
        result = retry(risky_operation)
        response_time = time.time() - start_time

        log_request("/data", {
            "response": result,
            "response_time": response_time
        })

        return result

    except Exception:
        failure_count += 1
        response_time = time.time() - start_time

        error = {"error": "Failed after retries"}

        log_request("/data", {
            "response": error,
            "response_time": response_time
        })

        return error

# ------------------ METRICS ------------------
@app.get("/metrics")
def metrics():
    return {
        "total_requests": request_count,
        "failures": failure_count,
        "success_rate": round((request_count - failure_count) / request_count, 2) if request_count else 0,
        "rate_limit": RATE_LIMIT,
        "failure_rate": FAILURE_RATE,
        "latency_range": DELAY_RANGE
    }

# ------------------ REPLAY ------------------
@app.get("/replay")
def replay():
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        return {"error": "No logs found"}

    return {
        "total_logs": len(logs),
        "recent_logs": logs[-5:]
    }

# ------------------ DASHBOARD ------------------
@app.get("/")
@app.get("/dashboard")
def dashboard():
    file_path = os.path.join(os.getcwd(), "templates", "dashboard.html")

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    return FileResponse(file_path)