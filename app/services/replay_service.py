import json
import os


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


class ReplayService:

    def __init__(self):

        self.frames = []

    # ---------------------------------------------------
    # Load Logs
    # ---------------------------------------------------

    def load_logs(self):

        try:

            with open(LOG_FILE, "r") as f:

                return json.load(f)

        except Exception:

            return []

    # ---------------------------------------------------
    # Build Replay Frames
    # ---------------------------------------------------

    def build_frames(self):

        logs = self.load_logs()

        self.frames = []

        total = 0

        success = 0

        failures = 0

        latency_sum = 0

        status_codes = {

            "200": 0,

            "429": 0,

            "500": 0

        }

        health = 100

        for log in logs:

            total += 1

            latency_sum += log.get(
                "latency_ms",
                0
            )

            status = log.get(
                "status",
                ""
            )

            if status == "SUCCESS":

                success += 1

                status_codes["200"] += 1

            elif status == "RATE_LIMITED":

                status_codes["429"] += 1

                failures += 1

                health -= 1

            else:

                status_codes["500"] += 1

                failures += 1

                health -= 2

            health = max(
                health,
                0
            )

            avg_latency = (

                latency_sum / total

            ) if total else 0

            success_rate = round(

                success / total * 100,

                1

            )

            frame = {

                "frame": total,

                "health": health,

                "total_requests": total,

                "success": success,

                "failures": failures,

                "success_rate": success_rate,

                "average_latency": round(

                    avg_latency,

                    2

                ),

                "status_codes": status_codes.copy(),

                "log": log

            }

            self.frames.append(
                frame
            )

        return self.frames


replay = ReplayService()