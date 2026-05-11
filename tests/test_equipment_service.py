import unittest

from models.booking import Booking
from models.transaction import Transaction
from services.equipment_service import EquipmentService
from tests.helpers import active_times, build_data_service


class EquipmentServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.student = self.ds.users["stu001"]
        self.service = EquipmentService(self.ds)

    def _add_active_booking(self):
        date, start_time, end_time = active_times()
        booking = Booking(
            booking_id="active001",
            booking_reference="BR-ACTIVE-001",
            student_id=self.student.user_id,
            room_id="rm001",
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration=1.0,
            total_cost=10.0,
            original_cost=10.0,
            status=Booking.STATUS_ACTIVE,
            payment_method=Booking.PAYMENT_BALANCE,
        )
        self.ds.bookings[booking.booking_id] = booking
        return booking

    def test_get_available_equipment_excludes_damaged_items(self):
        equipment = self.service.get_available_equipment("rm001")

        self.assertEqual(["eq001"], [item.equipment_id for item in equipment])

    def test_borrow_equipment_requires_existing_active_booking(self):
        success, message = self.service.borrow_equipment(self.student, "missing", "eq001")
        self.assertFalse(success)
        self.assertIn("Booking not found", message)

        future_booking = Booking(
            booking_id="future001",
            student_id=self.student.user_id,
            room_id="rm001",
            date="2999-01-01",
            start_time="09:00",
            end_time="10:00",
            status=Booking.STATUS_ACTIVE,
        )
        self.ds.bookings[future_booking.booking_id] = future_booking

        success, message = self.service.borrow_equipment(
            self.student, future_booking.booking_id, "eq001")
        self.assertFalse(success)
        self.assertIn("during your own active booking", message)

    def test_borrow_equipment_deducts_deposit_and_creates_loan(self):
        booking = self._add_active_booking()

        success, loan = self.service.borrow_equipment(
            self.student, booking.booking_id, "eq001")

        self.assertTrue(success)
        self.assertAlmostEqual(100.0, self.student.account_balance)
        self.assertFalse(self.ds.equipment["eq001"].is_available)
        self.assertIn(loan.loan_id, self.ds.equipment_loans)
        self.assertTrue(any(t.transaction_type == Transaction.TYPE_DEPOSIT_CHARGE
                            for t in self.ds.transactions.values()))

    def test_borrow_equipment_rejects_insufficient_deposit(self):
        booking = self._add_active_booking()
        self.student.account_balance = 99.99

        success, message = self.service.borrow_equipment(
            self.student, booking.booking_id, "eq001")

        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)

    def test_borrow_equipment_rejects_item_from_another_room(self):
        booking = self._add_active_booking()

        success, message = self.service.borrow_equipment(
            self.student, booking.booking_id, "eq003")

        self.assertFalse(success)
        self.assertIn("not available for this room", message)

    def test_return_equipment_refunds_deposit(self):
        booking = self._add_active_booking()
        _, loan = self.service.borrow_equipment(self.student, booking.booking_id, "eq001")

        success, message = self.service.return_equipment(self.student, loan.loan_id)

        self.assertTrue(success)
        self.assertTrue(loan.is_returned)
        self.assertTrue(self.ds.equipment["eq001"].is_available)
        self.assertAlmostEqual(200.0, self.student.account_balance)
        self.assertIn("deposit refunded", message)

    def test_return_damaged_equipment_forfeits_deposit(self):
        booking = self._add_active_booking()
        _, loan = self.service.borrow_equipment(self.student, booking.booking_id, "eq001")

        success, message = self.service.return_equipment(
            self.student, loan.loan_id, damaged=True)

        self.assertTrue(success)
        self.assertTrue(loan.is_damaged)
        self.assertTrue(self.ds.equipment["eq001"].is_damaged)
        self.assertAlmostEqual(100.0, self.student.account_balance)
        self.assertIn("forfeited", message)


if __name__ == "__main__":
    unittest.main()
