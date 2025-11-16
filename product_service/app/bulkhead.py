from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging
from typing import Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bulkhead:
    def __init__(self, name: str, max_workers: int = 5, timeout: int = 30):
        self.name = name
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=f"bulkhead-{name}-")
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        future = self.executor.submit(func, *args, **kwargs)
        return future.result(timeout=self.timeout)
    def shutdown(self):
        self.executor.shutdown(wait=True)

class BulkheadManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.bulkheads = {}
        return cls._instance
    def create_bulkhead(self, name: str, max_workers: int = 5, timeout: int = 30) -> Bulkhead:
        if name not in self.bulkheads:
            self.bulkheads[name] = Bulkhead(name, max_workers, timeout)
        return self.bulkheads[name]
    def get_bulkhead(self, name: str) -> Bulkhead:
        return self.bulkheads[name]
