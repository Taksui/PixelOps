import random
import time

from app.services.chaos_config import chaos_config


class ChaosEngine:

    def __init__(self):

        self.total_failures = 0
        self.total_timeouts = 0
        self.total_retries = 0

    # =====================================================
    # Network Latency + Jitter
    # =====================================================

    def inject_latency(self):

        latency = random.uniform(
            chaos_config.min_latency,
            chaos_config.max_latency
        )

        # Small network jitter
        latency += random.uniform(0, 0.15)

        time.sleep(latency)

        return latency

    # =====================================================
    # Failure
    # =====================================================

    def should_fail(self):

        fail = random.random() < chaos_config.failure_rate

        if fail:
            self.total_failures += 1

        return fail

    # =====================================================
    # Timeout
    # =====================================================

    def should_timeout(self):

        timeout = random.random() < chaos_config.timeout_rate

        if timeout:
            self.total_timeouts += 1

        return timeout

    # =====================================================
    # Packet Loss
    # =====================================================

    def packet_loss(self):

        # 5% packet loss

        return random.random() < 0.05

    # =====================================================
    # Retry Logic
    # =====================================================

    def retry(self, func):

        retries = chaos_config.retry_attempts

        for attempt in range(retries):

            try:

                # Simulate timeout
                if self.should_timeout():

                    raise TimeoutError("Simulated Timeout")

                # Simulate packet loss
                if self.packet_loss():

                    raise ConnectionError("Packet Lost")

                result = func()

                return result, attempt + 1

            except Exception:

                self.total_retries += 1

                if attempt == retries - 1:
                    raise

                backoff = (
                    chaos_config.retry_base_delay
                    * (2 ** attempt)
                )

                time.sleep(backoff)

    # =====================================================
    # Dashboard Stats
    # =====================================================

    def stats(self):

        return {

            "failures": self.total_failures,

            "timeouts": self.total_timeouts,

            "retries": self.total_retries

        }


chaos = ChaosEngine()