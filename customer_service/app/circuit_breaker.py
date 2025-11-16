import time
from enum import Enum

class State(Enum):
    CLOSED="CLOSED"
    OPEN="OPEN"
    HALF_OPEN="HALF_OPEN"

class CircuitBreakerError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_failures=3, open_timeout=30):
        self.max_failures = max_failures
        self.open_timeout = open_timeout
        self.fail_count = 0
        self.state = State.CLOSED
        self.last_failure_time = None
    def _update_state(self):
        if self.state == State.OPEN and (time.time() - self.last_failure_time) >= self.open_timeout:
            self.state = State.HALF_OPEN
    def call(self, func, *args, **kwargs):
        self._update_state()
        if self.state == State.OPEN:
            raise CircuitBreakerError("Circuito abierto")
        try:
            result = func(*args, **kwargs)
            self.fail_count = 0
            if self.state == State.HALF_OPEN:
                self.state = State.CLOSED
            return result
        except Exception:
            self.fail_count += 1
            self.last_failure_time = time.time()
            if self.fail_count >= self.max_failures:
                self.state = State.OPEN
            raise
