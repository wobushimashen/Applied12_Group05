import uuid


class Equipment:
    def __init__(self, equipment_id=None, room_id="", equipment_type="",
                 is_available=True, is_damaged=False):
        self.equipment_id = equipment_id or str(uuid.uuid4())[:8]
        self.room_id = room_id
        self.equipment_type = equipment_type
        self.is_available = is_available
        self.is_damaged = is_damaged

    def to_dict(self):
        return {
            "equipment_id": self.equipment_id,
            "room_id": self.room_id,
            "equipment_type": self.equipment_type,
            "is_available": str(self.is_available),
            "is_damaged": str(self.is_damaged),
        }
