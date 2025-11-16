import httpx, os
from .repo import OrderRepo

PRODUCT_URL = os.getenv("PRODUCT_URL", "http://localhost:8001")
CUSTOMER_URL = os.getenv("CUSTOMER_URL", "http://localhost:8003")

class OrderService:
    def __init__(self):
        self.repo = OrderRepo()
    def _verify_customer(self, client_id: int):
        r = httpx.get(f"{CUSTOMER_URL}/clientes/{client_id}", timeout=5)
        return r.status_code == 200
    def _verify_product(self, product_id: int):
        r = httpx.get(f"{PRODUCT_URL}/productos/{product_id}", timeout=5)
        return r.status_code == 200
    def create(self, data: dict):
        if not self._verify_customer(data["client_id"]):
            raise ValueError("Cliente no existe")
        for item in data["items"]:
            if not self._verify_product(item["product_id"]):
                raise ValueError(f"Producto {item['product_id']} no existe")
        return self.repo.save(data)
    def get(self, oid: int):
        return self.repo.find_by_id(oid)
    def list(self):
        return self.repo.find_all()
