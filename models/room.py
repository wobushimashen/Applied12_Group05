import uuid


class Room:
    TYPE_SMALL = "Small"
    TYPE_MEDIUM = "Medium"
    TYPE_LARGE = "Large"

    ROOM_TYPE_DEFAULTS = {
        TYPE_SMALL: {
            "min_capacity": 1,
            "capacity": 2,
            "standard_equipment": "1 table, 2 chairs",
            "price_per_hour": 10.0,
        },
        TYPE_MEDIUM: {
            "min_capacity": 3,
            "capacity": 6,
            "standard_equipment": "1 big table, 6 chairs, 1 whiteboard on the wall",
            "price_per_hour": 40.0,
        },
        TYPE_LARGE: {
            "min_capacity": 5,
            "capacity": 10,
            "standard_equipment": "1 meeting room table, 10 chairs, 1 built-in projector",
            "price_per_hour": 80.0,
        },
    }

    def __init__(self, room_id=None, room_name="", building_id="",
                 capacity=2, price_per_hour=10.0, is_available=True,
                 room_type="", standard_equipment="", opening_time="08:00",
                 closing_time="22:00"):
        self.room_id = room_id or str(uuid.uuid4())[:8]
        self.room_name = room_name
        self.building_id = building_id
        self.room_type = self.normalize_room_type(room_type, capacity)
        defaults = self.ROOM_TYPE_DEFAULTS[self.room_type]
        self.capacity = int(capacity or defaults["capacity"])
        self.price_per_hour = float(price_per_hour or defaults["price_per_hour"])
        self.is_available = is_available
        self.standard_equipment = standard_equipment or defaults["standard_equipment"]
        self.opening_time = opening_time or "08:00"
        self.closing_time = closing_time or "22:00"

    @classmethod
    def normalize_room_type(cls, room_type="", capacity=2):
        value = str(room_type or "").strip().title()
        if value in cls.ROOM_TYPE_DEFAULTS:
            return value
        try:
            cap = int(capacity)
        except (TypeError, ValueError):
            cap = 2
        if cap <= 2:
            return cls.TYPE_SMALL
        if cap <= 6:
            return cls.TYPE_MEDIUM
        return cls.TYPE_LARGE

    @classmethod
    def defaults_for_type(cls, room_type):
        return cls.ROOM_TYPE_DEFAULTS[cls.normalize_room_type(room_type)]

    @property
    def min_capacity(self):
        return self.ROOM_TYPE_DEFAULTS[self.room_type]["min_capacity"]

    @property
    def max_capacity(self):
        return self.capacity

    @property
    def minimum_duration_hours(self):
        return 0.5 if self.room_type == self.TYPE_SMALL else 2.0

    @property
    def advance_notice_hours(self):
        if self.room_type == self.TYPE_MEDIUM:
            return 3.0
        if self.room_type == self.TYPE_LARGE:
            return 24.0
        return 0.0

    @property
    def late_cancel_threshold_hours(self):
        if self.room_type == self.TYPE_MEDIUM:
            return 3.0
        if self.room_type == self.TYPE_LARGE:
            return 24.0
        return 0.5

    @property
    def late_cancel_refund_rate(self):
        if self.room_type == self.TYPE_LARGE:
            return 0.30
        return 0.50

    @property
    def no_show_refund_rate(self):
        return 0.20 if self.room_type == self.TYPE_SMALL else 0.0

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "building_id": self.building_id,
            "room_type": self.room_type,
            "capacity": str(self.capacity),
            "standard_equipment": self.standard_equipment,
            "price_per_hour": f"{self.price_per_hour:.2f}",
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "is_available": str(self.is_available),
        }


