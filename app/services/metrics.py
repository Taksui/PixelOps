from collections import defaultdict
from statistics import mean
import time


class MetricsManager:

    def reset(self):

    # keep increasing session number
        self.session_id += 1

    # rebuild metrics

        current_session = self.session_id

        self.__init__()

    # restore latest session

        self.session_id = current_session

    def __init__(self):

        # ==================================================
        # Request Counters
        # ==================================================

        self.request_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.rate_limited = 0

        # ==================================================
        # Latency
        # ==================================================

        self.response_times = []

        self.max_latency = 0
        self.min_latency = float("inf")

        # ==================================================
        # Retry Statistics
        # ==================================================

        self.retry_attempts = 0

        # ==================================================
        # Status Codes
        # ==================================================

        self.status_codes = defaultdict(int)

        # ==================================================
        # Server
        # ==================================================

        self.server_start = time.time()

        # ==================================================
        # Dashboard History
        # ==================================================

        self.request_history = []

        self.latency_history = []

        self.success_history = []

        self.failure_history = []

        self.health_history = []

        self.rps_history = []

        self.session_id = 1

        self.chaos_history = []

        self.rate_limit_history = []

    # ==================================================
    # Helpers
    # ==================================================

    def _trim(self):

        LIMIT = 50

        self.request_history = self.request_history[-LIMIT:]
        self.latency_history = self.latency_history[-LIMIT:]
        self.success_history = self.success_history[-LIMIT:]
        self.failure_history = self.failure_history[-LIMIT:]
        self.health_history = self.health_history[-LIMIT:]
        self.rps_history = self.rps_history[-LIMIT:]
        self.chaos_history = self.chaos_history[-LIMIT:]
        self.rate_limit_history = self.rate_limit_history[-LIMIT:]

    # ==================================================
    # Success
    # ==================================================

    def record_success(self, latency, attempts):

        self.request_count += 1
        self.success_count += 1

        self.retry_attempts += max(0, attempts - 1)

        self.response_times.append(latency)

        self.status_codes[200] += 1

        self.max_latency = max(self.max_latency, latency)
        self.min_latency = min(self.min_latency, latency)

        now = time.time()

        self.request_history.append(now)

        self.latency_history.append(round(latency * 1000, 2))

        self.success_history.append(self.success_count)

        self.failure_history.append(self.failure_count)

        self.health_history.append(self.health())

        self.chaos_history.append(self.chaos_level())

        self.rate_limit_history.append(self.rate_limited)

        self.rps_history.append(self.requests_per_second())

        self._trim()

    # ==================================================
    # Failure
    # ==================================================

    def record_failure(
        self,
        latency,
        attempts,
        status_code=500
    ):

        self.request_count += 1

        self.failure_count += 1

        self.retry_attempts += attempts

        self.response_times.append(latency)

        self.status_codes[status_code] += 1

        self.max_latency = max(self.max_latency, latency)
        self.min_latency = min(self.min_latency, latency)

        now = time.time()

        self.request_history.append(now)

        self.latency_history.append(round(latency * 1000, 2))

        self.success_history.append(self.success_count)

        self.failure_history.append(self.failure_count)

        self.health_history.append(self.health())

        self.chaos_history.append(self.chaos_level())

        self.rate_limit_history.append(self.rate_limited)

        self.rps_history.append(self.requests_per_second())

        self._trim()

    # ==================================================
    # Rate Limit
    # ==================================================

    def record_rate_limit(self):

        self.request_count += 1

        self.rate_limited += 1

        self.status_codes[429] += 1

        now = time.time()

        self.request_history.append(now)

        self.health_history.append(self.health())

        self.chaos_history.append(self.chaos_level())

        self.rate_limit_history.append(self.rate_limited)

        self.rps_history.append(self.requests_per_second())

        self._trim()

    # ==================================================
    # Calculations
    # ==================================================

    def average_latency(self):

        if not self.response_times:
            return 0

        return round(
            mean(self.response_times) * 1000,
            2
        )

    def success_rate(self):

        if self.request_count == 0:
            return 0

        return round(
            self.success_count /
            self.request_count *
            100,
            2
        )

    def error_rate(self):

        if self.request_count == 0:
            return 0

        return round(
            self.failure_count /
            self.request_count *
            100,
            2
        )

    def requests_per_second(self):

        now = time.time()

        return len([
            t
            for t in self.request_history
            if now - t <= 1
        ])

    def uptime(self):

        elapsed = int(
            time.time() - self.server_start
        )

        h = elapsed // 3600
        m = (elapsed % 3600) // 60
        s = elapsed % 60

        return f"{h:02}:{m:02}:{s:02}"

    # ==================================================
    # Dashboard Metrics
    # ==================================================

    def health(self):

        hp = 100

        hp -= self.failure_count * 4

        hp -= self.rate_limited

        return max(0, hp)

    def chaos_level(self):

        chaos = (
            self.failure_count * 5 +
            self.retry_attempts * 2 +
            self.rate_limited
        )

        return min(100, chaos)

    def system_status(self):

        hp = self.health()

        if hp > 80:
            return "ONLINE"

        if hp > 50:
            return "DEGRADED"

        return "CHAOS"

    # ==================================================
    # Export
    # ==================================================

    def to_dict(self):

        return {

            "session_id": self.session_id,

            "total_requests": self.request_count,

            "successes": self.success_count,

            "failures": self.failure_count,

            "rate_limited": self.rate_limited,

            "success_rate": self.success_rate(),

            "error_rate": self.error_rate(),

            "average_latency_ms": self.average_latency(),

            "max_latency_ms": round(
                self.max_latency * 1000,
                2
            ),

            "min_latency_ms":
                0 if self.min_latency == float("inf")
                else round(self.min_latency * 1000, 2),

            "requests_per_second":
                self.requests_per_second(),

            "uptime":
                self.uptime(),

            "retry_attempts":
                self.retry_attempts,

            "status_codes":
                dict(self.status_codes),

            "health":
                self.health(),

            "chaos_level":
                self.chaos_level(),

            "system_status":
                self.system_status(),

            "latency_history":
                self.latency_history,

            "success_history":
                self.success_history,

            "failure_history":
                self.failure_history,

            "health_history":
                self.health_history,

            "chaos_history":
                self.chaos_history,

            "rate_limit_history":
                self.rate_limit_history,

            "rps_history":
                self.rps_history
        }


metrics = MetricsManager()