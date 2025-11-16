import os
import json
import time
import pika
import httpx

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:pass@rabbitmq:5672/")
ORDER_QUEUE = os.getenv("ORDER_QUEUE", "orders")
SHIPPING_URL = os.getenv("SHIPPING_URL", "http://shipping_service:8005")

print(f"[WORKER] starting with RABBITMQ_URL={RABBITMQ_URL}, ORDER_QUEUE={ORDER_QUEUE}, SHIPPING_URL={SHIPPING_URL}")

def connect():
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 600
    return pika.BlockingConnection(params)

def process_message(payload: dict) -> bool:
    order_id = payload.get("order_id")
    if not order_id:
        print("[WORKER] mensaje sin order_id -> ack")
        return True
    try:
        # Simular trabajo
        time.sleep(0.2)
        # Crear envío para la orden
        url = f"{SHIPPING_URL}/envios"
        resp = httpx.post(url, json={"order_id": order_id}, timeout=5)
        if resp.status_code >= 400:
            print(f"[WORKER] fallo creando envío para orden {order_id}: {resp.status_code} {resp.text}")
            return False
        print(f"[WORKER] envío creado para orden {order_id}: {resp.json()}")
        return True
    except Exception as e:
        print(f"[WORKER] excepción procesando orden {order_id}: {e}")
        return False

def run():
    while True:
        try:
            conn = connect()
            ch = conn.channel()
            ch.queue_declare(queue=ORDER_QUEUE, durable=True)
            ch.basic_qos(prefetch_count=1)

            def _cb(ch_, method, properties, body):
                try:
                    payload = json.loads(body)
                except Exception:
                    print("[WORKER] payload inválido -> ack")
                    ch_.basic_ack(delivery_tag=method.delivery_tag)
                    return
                ok = process_message(payload)
                if ok:
                    ch_.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    # No requeue para evitar loops infinitos sencillos
                    ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            ch.basic_consume(queue=ORDER_QUEUE, on_message_callback=_cb, auto_ack=False)
            print("[WORKER] esperando mensajes...")
            ch.start_consuming()
        except Exception as e:
            print(f"[WORKER] conexión caída con RabbitMQ, reintentando en 3s: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run()
