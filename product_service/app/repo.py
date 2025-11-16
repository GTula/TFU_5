from .db import get_conn

class ProductRepo:
    def find_all(self):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM products")
            return [dict(r) for r in cur.fetchall()]
    def find_by_id(self, product_id: int):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    def save(self, data: dict):
        with get_conn() as conn:
            cur = conn.execute("INSERT INTO products (name, price, stock) VALUES (?,?,?)", (data["name"], data["price"], data["stock"]))
            conn.commit()
            return self.find_by_id(cur.lastrowid)
    def update(self, product_id: int, data: dict):
        with get_conn() as conn:
            conn.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (data["name"], data["price"], data["stock"], product_id))
            conn.commit()
            return self.find_by_id(product_id)
    def delete(self, product_id: int):
        with get_conn() as conn:
            cur = conn.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            return {"id": product_id} if cur.rowcount else None
