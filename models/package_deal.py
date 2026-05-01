import uuid
from datetime import datetime


class PackageDeal:
    def __init__(self, package_id=None, student_id="",
                 price=100.0, total_hours=12.0, remaining_hours=12.0,
                 purchase_date=""):
        self.package_id = package_id or str(uuid.uuid4())[:8]
        self.student_id = student_id
        self.price = float(price)
        self.total_hours = float(total_hours)
        self.remaining_hours = float(remaining_hours)
        self.purchase_date = purchase_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "package_id": self.package_id,
            "student_id": self.student_id,
            "price": f"{self.price:.2f}",
            "total_hours": f"{self.total_hours:.1f}",
            "remaining_hours": f"{self.remaining_hours:.1f}",
            "purchase_date": self.purchase_date,
        }
