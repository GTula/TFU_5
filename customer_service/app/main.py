from fastapi import FastAPI, HTTPException
from .db import init_db
from .service import CustomerService

app = FastAPI(title="Customer Service")
svc = CustomerService()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/clientes", status_code=201)
def registrar(data: dict):
    return svc.register(data)

@app.post("/clientes/login")
def login(data: dict):
    user = svc.login(data["email"], data["password"])
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    return user

@app.put("/clientes/{cliente_id}")
def actualizar(cliente_id: int, data: dict):
    updated = svc.update(cliente_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return updated

@app.get("/clientes/{cliente_id}")
def obtener(cliente_id: int):
    cli = svc.get(cliente_id)
    if not cli:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cli

@app.post("/clientes/{cliente_id}/pagos")
def pagar(cliente_id: int, data: dict):
    monto = data.get("monto")
    if not monto or monto <= 0:
        raise HTTPException(status_code=400, detail="Monto invalido")
    resultado = svc.pay(cliente_id, monto, data.get("metodo_pago","tarjeta"))
    if not resultado.get("exito", True):
        raise HTTPException(status_code=503, detail=resultado["mensaje"])
    return resultado
