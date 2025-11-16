from fastapi import FastAPI, HTTPException
from .service import PaymentService, PaymentProcessingError

app = FastAPI(title="Payment Service")
svc = PaymentService()

@app.post("/pagos", status_code=201)
def procesar(data: dict):
    try:
        return svc.process_payment(data["cliente_id"], data["monto"], data.get("metodo_pago","tarjeta"))
    except PaymentProcessingError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/pagos/{transaccion_id}")
def verificar(transaccion_id: str):
    return svc.verify(transaccion_id)

@app.get("/pagos/stats")
def stats():
    return svc.stats()

@app.post("/pagos/fail-rate")
def configurar(data: dict):
    rate = data.get("tasa_fallo",0.0)
    if rate <0 or rate>1:
        raise HTTPException(status_code=400, detail="tasa_fallo debe estar entre 0 y 1")
    svc.configure_fail_rate(rate)
    return {"tasa_fallo": rate}
