import threading
import time


class TrafficGenerator:

    def __init__(self):

        self.running = False

        self.thread = None

        self.rps = 5

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

    def run(self):

        while self.running:

            # We'll add requests here later

            time.sleep(1 / self.rps)


traffic = TrafficGenerator()