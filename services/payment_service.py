import math

from models.transaction import Transaction
from models.package_deal import PackageDeal


class PaymentService:
    def __init__(self, data_service):
        self.ds = data_service

    def add_funds(self, student, amount_str):
        try:
            amount = float(amount_str)
        except ValueError:
            return False, "Please enter a valid positive amount."

        if not math.isfinite(amount) or amount < 0.01:
            return False, "Please enter a valid positive amount."
        if amount > 1000:
            return False, "Maximum top-up amount is $1000 per transaction."

        student.account_balance += amount

        tx = Transaction(
            student_id=student.user_id,
            amount=amount,
            transaction_type=Transaction.TYPE_TOPUP,
            description=f"Account top-up of ${amount:.2f}",
        )
        self.ds.transactions[tx.transaction_id] = tx
        self.ds.save_all()
        return True, f"${amount:.2f} added successfully. New balance: ${student.account_balance:.2f}"

    def purchase_package_deal(self, student):
        if student.account_balance < 100:
            return False, (f"Insufficient funds. You need at least $100 to purchase "
                           f"a Package Deal. Your current balance is ${student.account_balance:.2f}.")

        student.account_balance -= 100

        package = PackageDeal(
            student_id=student.user_id,
            price=100.0,
            total_hours=12.0,
            remaining_hours=12.0,
        )
        self.ds.package_deals[package.package_id] = package

        tx = Transaction(
            student_id=student.user_id,
            amount=100,
            transaction_type=Transaction.TYPE_PACKAGE_PURCHASE,
            description="Package Deal purchase: $100 for 12 hours",
        )
        self.ds.transactions[tx.transaction_id] = tx
        self.ds.save_all()

        total_hours = self.ds.get_package_hours(student.user_id)
        return True, (f"Package Deal purchased! 12 hours added. "
                      f"Total package hours: {total_hours:.1f}. "
                      f"Remaining balance: ${student.account_balance:.2f}")

    def get_transaction_history(self, student_id):
        return [t for t in self.ds.transactions.values()
                if t.student_id == student_id]
