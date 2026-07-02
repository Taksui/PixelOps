from dataclasses import dataclass


@dataclass
class ChaosConfig:

    # ---------------------------------
    # Failure Simulation
    # ---------------------------------

    failure_rate: float = 0.30
    timeout_rate: float = 0.10

    # ---------------------------------
    # Artificial Latency (seconds)
    # ---------------------------------

    min_latency: float = 0.20
    max_latency: float = 1.50

    # ---------------------------------
    # Retry Settings
    # ---------------------------------

    retry_attempts: int = 3
    retry_base_delay: float = 0.5

    # ---------------------------------
    # Rate Limiting
    # ---------------------------------

    rate_limit: int = 5

    # ---------------------------------
    # Dashboard Metadata
    # ---------------------------------

    version: str = "2.1.0"

    # ==========================================
    # Runtime Update
    # ==========================================

    def update(self, data: dict):

        allowed = {
            "failure_rate",
            "timeout_rate",
            "min_latency",
            "max_latency",
            "retry_attempts",
            "retry_base_delay",
            "rate_limit"
        }

        for key, value in data.items():

            if key in allowed:

                setattr(self, key, value)

    # ==========================================
    # Export Current Config
    # ==========================================

    def to_dict(self):

        return {

            "failure_rate": self.failure_rate,

            "timeout_rate": self.timeout_rate,

            "min_latency": self.min_latency,

            "max_latency": self.max_latency,

            "retry_attempts": self.retry_attempts,

            "retry_base_delay": self.retry_base_delay,

            "rate_limit": self.rate_limit,

            "version": self.version
        }


chaos_config = ChaosConfig()