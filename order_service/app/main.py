from fastapi import FastAPI, HTTPException
from .db import init_db
from .service import OrderService

app = FastAPI(title="Order Service")
svc = OrderService()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/ordenes", status_code=201)
def crear(data: dict):
    if not data.get("client_id"):
        raise HTTPException(status_code=400, detail="Falta client_id")
    if not data.get("items"):
        raise HTTPException(status_code=400, detail="Faltan items")
    try:
        return svc.create(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/ordenes/{orden_id}")
def obtener(orden_id: int):
    o = svc.get(orden_id)
    if not o:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return o

@app.get("/ordenes")
def listar():
    return svc.list()
