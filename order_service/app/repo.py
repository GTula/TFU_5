from .db import get_conn

class OrderRepo:
    def save(self, data: dict):
        with get_conn() as conn:
            cur = conn.execute("INSERT INTO orders (client_id) VALUES (?)", (data["client_id"],))
            order_id = cur.lastrowid
            for item in data["items"]:
                conn.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?,?,?)", (order_id, item["product_id"], item["quantity"]))
            conn.commit()
            return self.find_by_id(order_id)
    def find_by_id(self, oid: int):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM orders WHERE id=?", (oid,))
            order = cur.fetchone()
            if not order:
                return None
            items_cur = conn.execute("SELECT * FROM order_items WHERE order_id=?", (oid,))
            items = [dict(r) for r in items_cur.fetchall()]
            o = dict(order)
            o["items"] = items
            return o
    def find_all(self):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM orders")
            orders = []
            for r in cur.fetchall():
                orders.append(self.find_by_id(r["id"]))
            return orders
