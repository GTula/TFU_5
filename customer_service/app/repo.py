from .db import get_conn

class CustomerRepo:
    def save(self, data: dict):
        with get_conn() as conn:
            cur = conn.execute("INSERT INTO clients (name,email,password,rol) VALUES (?,?,?,?)", (data["name"], data["email"], data["password"], data.get("rol","usuario")))
            conn.commit()
            return self.find_by_id(cur.lastrowid)
    def find_by_id(self, cid: int):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM clients WHERE id=?", (cid,))
            row = cur.fetchone()
            return dict(row) if row else None
    def login(self, email: str, password: str):
        with get_conn() as conn:
            cur = conn.execute("SELECT * FROM clients WHERE email=? AND password=?", (email,password))
            row = cur.fetchone()
            return dict(row) if row else None
    def update(self, cid: int, data: dict):
        with get_conn() as conn:
            conn.execute("UPDATE clients SET name=?, email=?, password=?, rol=? WHERE id=?", (data["name"], data["email"], data["password"], data.get("rol","usuario"), cid))
            conn.commit()
            return self.find_by_id(cid)
