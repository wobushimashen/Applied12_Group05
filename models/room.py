import uuid


class Room:
    def __init__(self, room_id=None, room_name="", building_id="",
                 capacity=2, price_per_hour=10.0, is_available=True):
        self.room_id = room_id or str(uuid.uuid4())[:8]
        self.room_name = room_name
        self.building_id = building_id
        self.capacity = int(capacity)
        self.price_per_hour = float(price_per_hour)
        self.is_available = is_available

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "building_id": self.building_id,
            "capacity": str(self.capacity),
            "price_per_hour": f"{self.price_per_hour:.2f}",
            "is_available": str(self.is_available),
        }
