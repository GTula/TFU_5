from fastapi import FastAPI, HTTPException
from .db import init_db
from .service import ShippingService

app = FastAPI(title="Shipping Service")
svc = ShippingService()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/envios", status_code=201)
def crear(data: dict):
    if not data.get("order_id"):
        raise HTTPException(status_code=400, detail="Falta order_id")
    return svc.create_shipment(data["order_id"])

@app.put("/envios/{shipment_id}")
def actualizar(shipment_id: int, data: dict):
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Falta status")
    sh = svc.update_shipment(shipment_id, status)
    if not sh:
        raise HTTPException(status_code=404, detail="Envio no encontrado")
    return sh

@app.get("/envios/{shipment_id}")
def obtener(shipment_id: int):
    sh = svc.get(shipment_id)
    if not sh:
        raise HTTPException(status_code=404, detail="Envio no encontrado")
    return sh

@app.get("/envios")
def listar():
    return svc.list()
