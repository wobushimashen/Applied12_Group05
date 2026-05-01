import uuid
from datetime import datetime


class EquipmentLoan:
    def __init__(self, loan_id=None, student_id="", booking_id="",
                 equipment_id="", deposit_amount=100.0,
                 is_returned=False, is_damaged=False, loan_date=""):
        self.loan_id = loan_id or str(uuid.uuid4())[:8]
        self.student_id = student_id
        self.booking_id = booking_id
        self.equipment_id = equipment_id
        self.deposit_amount = float(deposit_amount)
        self.is_returned = is_returned
        self.is_damaged = is_damaged
        self.loan_date = loan_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "student_id": self.student_id,
            "booking_id": self.booking_id,
            "equipment_id": self.equipment_id,
            "deposit_amount": f"{self.deposit_amount:.2f}",
            "is_returned": str(self.is_returned),
            "is_damaged": str(self.is_damaged),
            "loan_date": self.loan_date,
        }
