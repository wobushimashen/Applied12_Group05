from models.equipment_loan import EquipmentLoan
from models.transaction import Transaction


class EquipmentService:
    def __init__(self, data_service):
        self.ds = data_service

    def get_available_equipment(self, room_id):
        return [e for e in self.ds.get_equipment_by_room(room_id)
                if e.is_available and not e.is_damaged]

    def borrow_equipment(self, student, booking_id, equipment_id):
        booking = self.ds.bookings.get(booking_id)
        if not booking:
            return False, "Booking not found."
        if booking.student_id != student.user_id:
            return False, "This booking does not belong to you."
        if not booking.is_active_now():
            return False, "Equipment can only be borrowed during your own active booking."

        equipment = self.ds.equipment.get(equipment_id)
        if not equipment:
            return False, "Equipment not found."
        if not equipment.is_available or equipment.is_damaged:
            return False, "The selected equipment is no longer available. Please choose another item."

        if student.account_balance < 100:
            return False, "Insufficient funds for the equipment deposit ($100 required)."

        # Deduct deposit
        student.account_balance -= 100

        # Create transaction
        tx = Transaction(
            student_id=student.user_id,
            amount=100,
            transaction_type=Transaction.TYPE_DEPOSIT_CHARGE,
            description=f"Equipment deposit for {equipment.equipment_type} ({equipment.equipment_id})",
        )
        self.ds.transactions[tx.transaction_id] = tx

        # Create loan
        loan = EquipmentLoan(
            student_id=student.user_id,
            booking_id=booking_id,
            equipment_id=equipment_id,
            deposit_amount=100,
        )
        self.ds.equipment_loans[loan.loan_id] = loan

        # Mark equipment as borrowed
        equipment.is_available = False

        self.ds.save_all()
        return True, loan

    def return_equipment(self, student, loan_id, damaged=False):
        loan = self.ds.equipment_loans.get(loan_id)
        if not loan:
            return False, "Loan not found."
        if loan.student_id != student.user_id:
            return False, "This loan does not belong to you."
        if loan.is_returned:
            return False, "This equipment has already been returned."

        equipment = self.ds.equipment.get(loan.equipment_id)
        if not equipment:
            return False, "Equipment record not found."

        loan.is_returned = True

        if damaged:
            loan.is_damaged = True
            equipment.is_damaged = True
            # Deposit forfeited - no refund
            tx = Transaction(
                student_id=student.user_id,
                amount=0,
                transaction_type=Transaction.TYPE_DEPOSIT_CHARGE,
                description=f"Deposit forfeited - {equipment.equipment_type} returned damaged",
            )
            self.ds.transactions[tx.transaction_id] = tx
            self.ds.save_all()
            return True, "Deposit forfeited due to equipment damage."
        else:
            # Refund deposit
            student.account_balance += loan.deposit_amount
            equipment.is_available = True
            tx = Transaction(
                student_id=student.user_id,
                amount=loan.deposit_amount,
                transaction_type=Transaction.TYPE_DEPOSIT_REFUND,
                description=f"Equipment deposit refund for {equipment.equipment_type}",
            )
            self.ds.transactions[tx.transaction_id] = tx
            self.ds.save_all()
            return True, f"Equipment returned. ${loan.deposit_amount:.2f} deposit refunded."

    def get_active_loans_for_student(self, student_id):
        return [el for el in self.ds.equipment_loans.values()
                if el.student_id == student_id and not el.is_returned]

    def get_loans_for_booking(self, booking_id):
        return self.ds.get_equipment_loans_for_booking(booking_id)
