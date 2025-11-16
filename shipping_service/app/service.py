from .repo import ShippingRepo

class ShippingService:
    def __init__(self):
        self.repo = ShippingRepo()
    def create_shipment(self, order_id: int):
        return self.repo.create(order_id)
    def update_shipment(self, shipment_id: int, status: str):
        return self.repo.update_status(shipment_id, status)
    def get(self, shipment_id: int):
        return self.repo.find_by_id(shipment_id)
    def list(self):
        return self.repo.find_all()
