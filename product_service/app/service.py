from .repo import ProductRepo
from .bulkhead import BulkheadManager
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        manager = BulkheadManager()
        manager.create_bulkhead("productos", max_workers=5, timeout=30)
        self.bulkhead = manager.get_bulkhead("productos")
        self.repo = ProductRepo()
    def list_products(self):
        return self.bulkhead.execute(self.repo.find_all)
    def get_product(self, product_id: int):
        return self.bulkhead.execute(self.repo.find_by_id, product_id)
    def add_product(self, data: dict):
        return self.bulkhead.execute(self.repo.save, data)
    def update_product(self, product_id: int, data: dict):
        return self.bulkhead.execute(self.repo.update, product_id, data)
    def delete_product(self, product_id: int):
        return self.bulkhead.execute(self.repo.delete, product_id)
