import httpx, os
from .repo import CustomerRepo
from .circuit_breaker import CircuitBreaker, CircuitBreakerError

PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8002")

class CustomerService:
    def __init__(self):
        self.repo = CustomerRepo()
        self.cb = CircuitBreaker(max_failures=3, open_timeout=20)
    def register(self, data: dict):
        return self.repo.save(data)
    def login(self, email: str, password: str):
        return self.repo.login(email, password)
    def update(self, cid: int, data: dict):
        return self.repo.update(cid, data)
    def get(self, cid: int):
        return self.repo.find_by_id(cid)
    def pay(self, cid: int, monto: float, metodo: str="tarjeta"):
        def _call():
            resp = httpx.post(f"{PAYMENT_URL}/pagos", json={"cliente_id": cid, "monto": monto, "metodo_pago": metodo}, timeout=5)
            resp.raise_for_status()
            return resp.json()
        try:
            return self.cb.call(_call)
        except CircuitBreakerError:
            return {"exito": False, "mensaje": "Servicio de pagos no disponible"}
        except httpx.HTTPError as e:
            return {"exito": False, "mensaje": f"Error procesando pago: {e}"}
