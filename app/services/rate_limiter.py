import time
from collections import defaultdict


class RateLimiter:

    def __init__(self):

        # client_ip -> request timestamps
        self.clients = defaultdict(list)

        # Sliding window (seconds)
        self.window = 10

    # =====================================================
    # Allow Request
    # =====================================================

    def allow_request(self, client_ip: str, limit: int):

        now = time.time()

        # Remove expired timestamps
        self.clients[client_ip] = [

            timestamp

            for timestamp in self.clients[client_ip]

            if now - timestamp < self.window

        ]

        # Check limit
        if len(self.clients[client_ip]) >= limit:

            return False

        # Record request
        self.clients[client_ip].append(now)

        return True

    # =====================================================
    # Requests Remaining
    # =====================================================

    def remaining_requests(self, client_ip: str, limit: int):

        now = time.time()

        self.clients[client_ip] = [

            timestamp

            for timestamp in self.clients[client_ip]

            if now - timestamp < self.window

        ]

        remaining = limit - len(self.clients[client_ip])

        return max(0, remaining)

    # =====================================================
    # Reset Single Client
    # =====================================================

    def reset_client(self, client_ip: str):

        self.clients.pop(client_ip, None)

    # =====================================================
    # Reset Everyone
    # =====================================================

    def reset_all(self):

        self.clients.clear()


rate_limiter = RateLimiter()