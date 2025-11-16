import httpx, os, json
import pika
from .repo import OrderRepo

PRODUCT_URL = os.getenv("PRODUCT_URL", "http://localhost:8001")
CUSTOMER_URL = os.getenv("CUSTOMER_URL", "http://localhost:8003")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:pass@rabbitmq:5672/")
ORDER_QUEUE = os.getenv("ORDER_QUEUE", "orders")

def _publish_order_event(order_id: int, payload: dict | None = None):
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 600
    conn = pika.BlockingConnection(params)
    try:
        ch = conn.channel()
        ch.queue_declare(queue=ORDER_QUEUE, durable=True)
        body = json.dumps({"order_id": order_id, "payload": payload or {}})
        ch.basic_publish(
            exchange="",
            routing_key=ORDER_QUEUE,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        try:
            conn.close()
        except Exception:
            pass

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
        order = self.repo.save(data)
        try:
            _publish_order_event(order_id=order["id"], payload={"client_id": order["client_id"]})
        except Exception as e:
            # No abortamos la creación de la orden si el broker no está disponible
            print(f"[ORDER_SERVICE] No se pudo publicar evento de orden {order['id']}: {e}")
        return order
    def get(self, oid: int):
        return self.repo.find_by_id(oid)
    def list(self):
        return self.repo.find_all()
