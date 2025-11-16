import os, jwt
from fastapi import FastAPI, HTTPException, Request, Header
import httpx
from typing import Optional

app = FastAPI(title="API Gateway")

PRODUCT_URL = os.getenv("PRODUCT_URL")
CUSTOMER_URL = os.getenv("CUSTOMER_URL")
ORDER_URL = os.getenv("ORDER_URL")
PAYMENT_URL = os.getenv("PAYMENT_URL")
SHIPPING_URL = os.getenv("SHIPPING_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"

async def proxy(method: str, url: str, json=None):
    async with httpx.AsyncClient() as client:
        r = await client.request(method, url, json=json)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

def create_token(user: dict):
    payload = {"usuario_id": user["id"], "email": user["email"], "rol": user.get("rol","usuario")}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verify_token(token: Optional[str]):
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")

@app.post("/auth/login")
async def login(data: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{CUSTOMER_URL}/clientes/login", json=data)
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Credenciales invalidas")
        user = r.json()
        token = create_token(user)
        return {"token": token, "usuario_id": user["id"], "email": user["email"], "rol": user.get("rol","usuario")}

# PRODUCTOS
@app.get("/productos")
async def listar_productos():
    return await proxy("GET", f"{PRODUCT_URL}/productos")

@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: int):
    return await proxy("GET", f"{PRODUCT_URL}/productos/{producto_id}")

@app.post("/productos")
async def crear_producto(data: dict, authorization: Optional[str] = Header(None)):
    claims = verify_token(authorization)
    return await proxy("POST", f"{PRODUCT_URL}/productos", json=data)

@app.put("/productos/{producto_id}")
async def actualizar_producto(producto_id: int, data: dict, authorization: Optional[str] = Header(None)):
    claims = verify_token(authorization)
    if claims.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Requiere rol admin")
    return await proxy("PUT", f"{PRODUCT_URL}/productos/{producto_id}", json=data)

@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int, authorization: Optional[str] = Header(None)):
    claims = verify_token(authorization)
    if claims.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Requiere rol admin")
    return await proxy("DELETE", f"{PRODUCT_URL}/productos/{producto_id}")

# CLIENTES (exponer subset)
@app.post("/clientes")
async def registrar_cliente(data: dict):
    return await proxy("POST", f"{CUSTOMER_URL}/clientes", json=data)

@app.get("/clientes/{cliente_id}")
async def obtener_cliente(cliente_id: int):
    return await proxy("GET", f"{CUSTOMER_URL}/clientes/{cliente_id}")

# PAGOS
@app.post("/clientes/{cliente_id}/pagos")
async def procesar_pago(cliente_id: int, data: dict):
    payload = {"cliente_id": cliente_id, "monto": data["monto"], "metodo_pago": data.get("metodo_pago","tarjeta")}
    return await proxy("POST", f"{PAYMENT_URL}/pagos", json=payload)

# ORDENES
@app.post("/ordenes")
async def crear_orden(data: dict):
    return await proxy("POST", f"{ORDER_URL}/ordenes", json=data)

@app.get("/ordenes")
async def listar_ordenes():
    return await proxy("GET", f"{ORDER_URL}/ordenes")

# ENVIOS
@app.post("/envios")
async def crear_envio(data: dict):
    return await proxy("POST", f"{SHIPPING_URL}/envios", json=data)

@app.get("/envios")
async def listar_envios():
    return await proxy("GET", f"{SHIPPING_URL}/envios")
