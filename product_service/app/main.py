from fastapi import FastAPI, HTTPException
from .db import init_db
from .service import ProductService

app = FastAPI(title="Product Service")
service = ProductService()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/productos")
def listar():
    return service.list_products()

@app.get("/productos/{producto_id}")
def obtener(producto_id: int):
    prod = service.get_product(producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@app.post("/productos", status_code=201)
def crear(data: dict):
    return service.add_product(data)

@app.put("/productos/{producto_id}")
def actualizar(producto_id: int, data: dict):
    updated = service.update_product(producto_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return updated

@app.delete("/productos/{producto_id}")
def eliminar(producto_id: int):
    deleted = service.delete_product(producto_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return deleted
