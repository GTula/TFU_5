from .db import get_conn

class ShippingRepo:
    def create(self, order_id: int):
        with get_conn() as conn:
            cur = conn.execute("INSERT INTO shipments (order_id) VALUES (?)", (order_id,))
            sid = cur.lastrowid
            conn.commit()
            return self.find_by_id(sid)
    def update_status(self, shipment_id: int, status: str):
        with get_conn() as conn:
            conn.execute("UPDATE shipments SET status=? WHERE id=?", (status, shipment_id))
            conn.commit()
            return self.find_by_id(shipment_id)
    def find_by_id(self, shipment_id: int):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM shipments WHERE id=?", (shipment_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    def find_all(self):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM shipments")
            return [dict(r) for r in cur.fetchall()]
