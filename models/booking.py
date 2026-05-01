import uuid
from datetime import datetime


class Booking:
    STATUS_ACTIVE = "Active"
    STATUS_CANCELLED = "Cancelled"
    STATUS_COMPLETED = "Completed"
    STATUS_NO_SHOW = "NoShow"

    PAYMENT_BALANCE = "AccountBalance"
    PAYMENT_PACKAGE = "PackageHours"

    def __init__(self, booking_id=None, booking_reference="", student_id="",
                 room_id="", date="", start_time="", end_time="",
                 duration=0.0, total_cost=0.0, original_cost=0.0, status="",
                 payment_method="", created_at=""):
        self.booking_id = booking_id or str(uuid.uuid4())[:8]
        self.booking_reference = booking_reference or self._generate_reference()
        self.student_id = student_id
        self.room_id = room_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.duration = float(duration)
        self.total_cost = float(total_cost)
        self.original_cost = float(original_cost) if original_cost else float(total_cost)
        self.status = status or self.STATUS_ACTIVE
        self.payment_method = payment_method
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _generate_reference(self):
        return f"BR-{datetime.now().strftime('%y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    def is_future(self):
        try:
            booking_datetime = datetime.strptime(f"{self.date} {self.end_time}", "%Y-%m-%d %H:%M")
            return datetime.now() < booking_datetime and self.status == self.STATUS_ACTIVE
        except ValueError:
            return False

    def is_active_now(self):
        try:
            start = datetime.strptime(f"{self.date} {self.start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{self.date} {self.end_time}", "%Y-%m-%d %H:%M")
            now = datetime.now()
            return start <= now <= end and self.status == self.STATUS_ACTIVE
        except ValueError:
            return False

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "booking_reference": self.booking_reference,
            "student_id": self.student_id,
            "room_id": self.room_id,
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": f"{self.duration:.1f}",
            "total_cost": f"{self.total_cost:.2f}",
            "original_cost": f"{self.original_cost:.2f}",
            "status": self.status,
            "payment_method": self.payment_method,
            "created_at": self.created_at,
        }
