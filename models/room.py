import uuid


class Room:
    TYPE_SMALL = "Small"
    TYPE_MEDIUM = "Medium"
    TYPE_LARGE = "Large"

    TYPE_DEFAULTS = {
        TYPE_SMALL: {
            "capacity_min": 1,
            "capacity_max": 2,
            "standard_equipment": "1 table, 2 chairs",
            "price_per_hour": 10.0,
            "minimum_duration": 0.5,
            "advance_notice_hours": 0.0,
            "late_cancellation_refund_rate": 0.50,
            "no_show_refund_rate": 0.20,
        },
        TYPE_MEDIUM: {
            "capacity_min": 3,
            "capacity_max": 6,
            "standard_equipment": "1 big table, 6 chairs, 1 whiteboard on the wall",
            "price_per_hour": 40.0,
            "minimum_duration": 2.0,
            "advance_notice_hours": 3.0,
            "late_cancellation_refund_rate": 0.50,
            "no_show_refund_rate": 0.0,
        },
        TYPE_LARGE: {
            "capacity_min": 5,
            "capacity_max": 10,
            "standard_equipment": "1 meeting room table, 10 chairs, 1 built-in projector",
            "price_per_hour": 80.0,
            "minimum_duration": 2.0,
            "advance_notice_hours": 24.0,
            "late_cancellation_refund_rate": 0.30,
            "no_show_refund_rate": 0.0,
        },
    }

    def __init__(self, room_id=None, room_name="", building_id="",
                 capacity=2, price_per_hour=None, is_available=True,
                 room_type="", capacity_min=None, capacity_max=None,
                 standard_equipment="", opening_time="08:00",
                 closing_time="22:00", minimum_duration=None,
                 advance_notice_hours=None,
                 late_cancellation_refund_rate=None,
                 no_show_refund_rate=None,
                 late_cancellation_threshold_minutes=30):
        self.room_id = room_id or str(uuid.uuid4())[:8]
        self.room_name = room_name
        self.building_id = building_id
        self.room_type = self.normalize_room_type(room_type) or self.infer_room_type(capacity)

        defaults = self.TYPE_DEFAULTS[self.room_type]
        self.capacity_min = int(capacity_min) if capacity_min not in (None, "") else defaults["capacity_min"]
        self.capacity_max = int(capacity_max) if capacity_max not in (None, "") else defaults["capacity_max"]
        self.capacity = int(capacity) if capacity not in (None, "") else self.capacity_max
        if self.capacity < self.capacity_min or self.capacity > self.capacity_max:
            self.capacity = self.capacity_max

        default_price = defaults["price_per_hour"]
        self.price_per_hour = float(price_per_hour) if price_per_hour not in (None, "") else default_price
        self.is_available = is_available
        self.standard_equipment = standard_equipment or defaults["standard_equipment"]
        self.opening_time = opening_time or "08:00"
        self.closing_time = closing_time or "22:00"
        self.minimum_duration = (
            float(minimum_duration)
            if minimum_duration not in (None, "")
            else defaults["minimum_duration"]
        )
        self.advance_notice_hours = (
            float(advance_notice_hours)
            if advance_notice_hours not in (None, "")
            else defaults["advance_notice_hours"]
        )
        self.late_cancellation_refund_rate = (
            float(late_cancellation_refund_rate)
            if late_cancellation_refund_rate not in (None, "")
            else defaults["late_cancellation_refund_rate"]
        )
        self.no_show_refund_rate = (
            float(no_show_refund_rate)
            if no_show_refund_rate not in (None, "")
            else defaults["no_show_refund_rate"]
        )
        self.late_cancellation_threshold_minutes = int(late_cancellation_threshold_minutes or 30)

    @classmethod
    def normalize_room_type(cls, room_type):
        value = (room_type or "").strip().lower()
        if value == "small":
            return cls.TYPE_SMALL
        if value == "medium":
            return cls.TYPE_MEDIUM
        if value == "large":
            return cls.TYPE_LARGE
        return ""

    @classmethod
    def infer_room_type(cls, capacity):
        try:
            capacity = int(capacity)
        except (TypeError, ValueError):
            return cls.TYPE_SMALL

        if capacity <= 2:
            return cls.TYPE_SMALL
        if capacity <= 6:
            return cls.TYPE_MEDIUM
        return cls.TYPE_LARGE

    @property
    def capacity_range(self):
        return f"{self.capacity_min}-{self.capacity_max}"

    def supports_party_size(self, party_size):
        try:
            party_size = int(party_size)
        except (TypeError, ValueError):
            return False
        return self.capacity_min <= party_size <= self.capacity_max

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "building_id": self.building_id,
            "room_type": self.room_type,
            "capacity_min": str(self.capacity_min),
            "capacity_max": str(self.capacity_max),
            "capacity": str(self.capacity),
            "standard_equipment": self.standard_equipment,
            "price_per_hour": f"{self.price_per_hour:.2f}",
            "standard_equipment": self.standard_equipment,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "minimum_duration": f"{self.minimum_duration:.1f}",
            "advance_notice_hours": f"{self.advance_notice_hours:.1f}",
            "late_cancellation_refund_rate": f"{self.late_cancellation_refund_rate:.2f}",
            "no_show_refund_rate": f"{self.no_show_refund_rate:.2f}",
            "late_cancellation_threshold_minutes": str(self.late_cancellation_threshold_minutes),
            "is_available": str(self.is_available),
        }


