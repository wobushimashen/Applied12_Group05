import unittest
from datetime import datetime, timedelta

from models.booking import Booking
from models.equipment_loan import EquipmentLoan
from services.booking_service import BookingService
from tests.helpers import add_future_booking, build_data_service, past_date


class BookingCancellationServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.student = self.ds.users["stu001"]
        self.service = BookingService(self.ds)

    def test_cancel_booking_refunds_account_balance(self):
        booking = add_future_booking(self.ds, self.student, room_id="rm001", days=2,
                                     payment_method=Booking.PAYMENT_BALANCE,
                                     total_cost=20.0)
        self.student.account_balance = 180.0

        success, message = self.service.cancel_booking(self.student, booking.booking_id)

        self.assertTrue(success)
        self.assertEqual(Booking.STATUS_CANCELLED, booking.status)
        self.assertAlmostEqual(200.0, self.student.account_balance)
        self.assertIn("Full refund", message)

    def test_cancel_booking_refunds_discounted_amount_only(self):
        booking = add_future_booking(self.ds, self.student, room_id="rm001", days=2,
                                     payment_method=Booking.PAYMENT_BALANCE,
                                     total_cost=16.0)
        booking.original_cost = 20.0
        self.student.account_balance = 84.0

        success, message = self.service.cancel_booking(self.student, booking.booking_id)

        self.assertTrue(success)
        self.assertAlmostEqual(100.0, self.student.account_balance)
        self.assertIn("$16.00", message)

    def test_cancel_booking_restores_package_hours(self):
        booking = add_future_booking(self.ds, self.student, room_id="rm001", days=2,
                                     payment_method=Booking.PAYMENT_PACKAGE,
                                     total_cost=20.0)
        self.ds.package_deals["pkg001"].remaining_hours = 3.0

        success, message = self.service.cancel_booking(self.student, booking.booking_id)

        self.assertTrue(success)
        self.assertEqual(Booking.STATUS_CANCELLED, booking.status)
        self.assertAlmostEqual(5.0, self.ds.get_package_hours(self.student.user_id))
        self.assertIn("Package hours", message)

    def test_late_cancellation_adds_strike(self):
        soon = datetime.now() + timedelta(minutes=20)
        booking = Booking(
            booking_id="late001",
            booking_reference="BR-LATE-001",
            student_id=self.student.user_id,
            room_id="rm001",
            date=soon.strftime("%Y-%m-%d"),
            start_time=soon.strftime("%H:%M"),
            end_time=(soon + timedelta(hours=1)).strftime("%H:%M"),
            duration=1.0,
            total_cost=10.0,
            original_cost=10.0,
            status=Booking.STATUS_ACTIVE,
            payment_method=Booking.PAYMENT_BALANCE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.student.account_balance = 190.0

        success, message = self.service.cancel_booking(self.student, booking.booking_id)

        self.assertTrue(success)
        self.assertEqual(1, self.student.late_cancellation_count)
        self.assertAlmostEqual(195.0, self.student.account_balance)
        self.assertIn("Late Cancellation", message)

    def test_late_large_room_cancellation_uses_30_percent_refund_rate(self):
        soon = datetime.now() + timedelta(minutes=20)
        booking = Booking(
            booking_id="late-large",
            booking_reference="BR-LATE-LARGE",
            student_id=self.student.user_id,
            room_id="rm004",
            date=soon.strftime("%Y-%m-%d"),
            start_time=soon.strftime("%H:%M"),
            end_time=(soon + timedelta(hours=2)).strftime("%H:%M"),
            duration=2.0,
            total_cost=160.0,
            original_cost=160.0,
            status=Booking.STATUS_ACTIVE,
            payment_method=Booking.PAYMENT_BALANCE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.student.account_balance = 40.0

        success, message = self.service.cancel_booking(self.student, booking.booking_id)

        self.assertTrue(success)
        self.assertAlmostEqual(88.0, self.student.account_balance)
        self.assertEqual(1, self.student.late_cancellation_count)
        self.assertIn("30% refund", message)

    def test_started_booking_is_not_future(self):
        start = datetime.now() - timedelta(minutes=10)
        booking = Booking(
            student_id=self.student.user_id,
            room_id="rm001",
            date=start.strftime("%Y-%m-%d"),
            start_time=start.strftime("%H:%M"),
            end_time=(start + timedelta(hours=1)).strftime("%H:%M"),
            status=Booking.STATUS_ACTIVE,
        )

        self.assertFalse(booking.is_future())
        self.assertTrue(booking.is_active_now())

    def test_mark_no_show_admin_updates_status_and_strike(self):
        booking = Booking(
            booking_id="past001",
            booking_reference="BR-PAST-001",
            student_id=self.student.user_id,
            room_id="rm001",
            date=past_date(),
            start_time="09:00",
            end_time="10:00",
            total_cost=10.0,
            status=Booking.STATUS_ACTIVE,
            payment_method=Booking.PAYMENT_BALANCE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.student.account_balance = 90.0

        success, message = self.service.mark_no_show_admin(booking.booking_id)

        self.assertTrue(success)
        self.assertEqual(Booking.STATUS_NO_SHOW, booking.status)
        self.assertAlmostEqual(92.0, self.student.account_balance)
        self.assertEqual(1, self.student.no_show_count)
        self.assertIn("marked as No-Show", message)

    def test_no_show_detection_ignores_booking_with_returned_equipment_loan(self):
        booking = Booking(
            booking_id="past-loan",
            booking_reference="BR-PAST-LOAN",
            student_id=self.student.user_id,
            room_id="rm001",
            date=past_date(),
            start_time="09:00",
            end_time="10:00",
            status=Booking.STATUS_ACTIVE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.ds.equipment_loans["loan-returned"] = EquipmentLoan(
            loan_id="loan-returned",
            student_id=self.student.user_id,
            booking_id=booking.booking_id,
            equipment_id="eq001",
            is_returned=True,
        )

        no_shows = self.service.check_no_shows()

        self.assertEqual([], no_shows)
        self.assertEqual(Booking.STATUS_ACTIVE, booking.status)
        self.assertEqual(0, self.student.no_show_count)

    def test_mark_no_show_admin_rejects_booking_with_equipment_loan(self):
        booking = Booking(
            booking_id="past-loan",
            booking_reference="BR-PAST-LOAN",
            student_id=self.student.user_id,
            room_id="rm001",
            date=past_date(),
            start_time="09:00",
            end_time="10:00",
            status=Booking.STATUS_ACTIVE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.ds.equipment_loans["loan-returned"] = EquipmentLoan(
            loan_id="loan-returned",
            student_id=self.student.user_id,
            booking_id=booking.booking_id,
            equipment_id="eq001",
            is_returned=True,
        )

        success, message = self.service.mark_no_show_admin(booking.booking_id)

        self.assertFalse(success)
        self.assertIn("equipment was borrowed", message)
        self.assertEqual(Booking.STATUS_ACTIVE, booking.status)
        self.assertEqual(0, self.student.no_show_count)

    def test_overdue_bookings_exclude_booking_with_equipment_loan(self):
        booking = Booking(
            booking_id="past-loan",
            booking_reference="BR-PAST-LOAN",
            student_id=self.student.user_id,
            room_id="rm001",
            date=past_date(),
            start_time="09:00",
            end_time="10:00",
            status=Booking.STATUS_ACTIVE,
        )
        self.ds.bookings[booking.booking_id] = booking
        self.ds.equipment_loans["loan-returned"] = EquipmentLoan(
            loan_id="loan-returned",
            student_id=self.student.user_id,
            booking_id=booking.booking_id,
            equipment_id="eq001",
            is_returned=True,
        )

        self.assertNotIn(booking, self.service.get_overdue_bookings())


if __name__ == "__main__":
    unittest.main()
