import uuid
from datetime import datetime


class Transaction:
    TYPE_TOPUP = "TopUp"
    TYPE_BOOKING_PAYMENT = "BookingPayment"
    TYPE_DEPOSIT_CHARGE = "DepositCharge"
    TYPE_DEPOSIT_REFUND = "DepositRefund"
    TYPE_PACKAGE_PURCHASE = "PackagePurchase"
    TYPE_PROMO_DISCOUNT = "PromoDiscount"
    TYPE_BOOKING_REFUND = "BookingRefund"

    def __init__(self, transaction_id=None, student_id="",
                 amount=0.0, transaction_type="",
                 transaction_date="", description=""):
        self.transaction_id = transaction_id or str(uuid.uuid4())[:8]
        self.student_id = student_id
        self.amount = float(amount)
        self.transaction_type = transaction_type
        self.transaction_date = transaction_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = description

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "student_id": self.student_id,
            "amount": f"{self.amount:.2f}",
            "transaction_type": self.transaction_type,
            "transaction_date": self.transaction_date,
            "description": self.description,
        }
