import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "data",
    "logs.json"
)

os.makedirs(
    os.path.dirname(LOG_FILE),
    exist_ok=True
)


class Logger:

    def __init__(self):

        self.max_logs = 500

    # =====================================================
    # Read Logs
    # =====================================================

    def read_logs(self):

        try:

            with open(LOG_FILE, "r") as f:

                return json.load(f)

        except Exception:

            return []

    # =====================================================
    # Save Logs
    # =====================================================

    def save_logs(self, logs):

        with open(LOG_FILE, "w") as f:

            json.dump(
                logs,
                f,
                indent=2
            )

    # =====================================================
    # Log Request
    # =====================================================

    def log_request(
        self,
        endpoint,
        client_ip,
        status,
        latency,
        response,
        attempts=1
    ):

        logs = self.read_logs()

        entry = {

            "timestamp":
                datetime.now().isoformat(),

            "endpoint":
                endpoint,

            "client_ip":
                client_ip,

            "status":
                status,

            "latency_ms":
                round(
                    latency * 1000,
                    2
                ),

            "attempts":
                attempts,

            "response":
                response

        }

        logs.append(entry)

        logs = logs[-self.max_logs:]

        self.save_logs(logs)

    # =====================================================
    # Recent Logs
    # =====================================================

    def recent(self, count=20):

        logs = self.read_logs()

        return logs[-count:]

    # =====================================================
    # Clear Logs
    # =====================================================

    def clear(self):

        self.save_logs([])


logger = Logger()


# ---------------------------------------------------------
# Backward Compatibility
# ---------------------------------------------------------

def log_request(
    endpoint,
    client_ip,
    status,
    latency,
    response,
    attempts=1
):

    logger.log_request(
        endpoint,
        client_ip,
        status,
        latency,
        response,
        attempts
    )