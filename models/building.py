import uuid


class Building:
    def __init__(self, building_id=None, building_name=""):
        self.building_id = building_id or str(uuid.uuid4())[:8]
        self.building_name = building_name

    def to_dict(self):
        return {
            "building_id": self.building_id,
            "building_name": self.building_name,
        }
