import time, random

class PaymentProcessingError(Exception):
    pass

class PaymentService:
    def __init__(self, fail_rate: float = 0.0, latency_ms: int = 100):
        self.fail_rate = fail_rate
        self.latency_ms = latency_ms
        self.processed = 0
        self.failed = 0
    def process_payment(self, client_id: int, amount: float, method: str = "tarjeta"):
        time.sleep(self.latency_ms/1000)
        if random.random() < self.fail_rate:
            self.failed += 1
            raise PaymentProcessingError("Fallo en el procesamiento del pago")
        self.processed += 1
        txn_id = f"TXN-{int(time.time())}-{random.randint(1000,9999)}"
        return {"transaccion_id": txn_id, "cliente_id": client_id, "monto": amount, "metodo_pago": method, "estado": "APROBADO"}
    def verify(self, txn_id: str):
        time.sleep(0.05)
        return {"transaccion_id": txn_id, "estado": "COMPLETADO"}
    def stats(self):
        total = self.processed + self.failed
        success = (self.processed/total*100) if total else 100.0
        return {"procesados": self.processed, "fallidos": self.failed, "tasa_exito": round(success,2)}
    def configure_fail_rate(self, rate: float):
        self.fail_rate = rate
