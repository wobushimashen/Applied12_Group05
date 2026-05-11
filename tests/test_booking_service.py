import unittest
from datetime import datetime, timedelta

from models.booking import Booking
from models.package_deal import PackageDeal
from models.transaction import Transaction
from services.booking_service import BookingService
from tests.helpers import add_future_booking, build_data_service, future_date, past_date


class BookingServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.student = self.ds.users["stu001"]
        self.service = BookingService(self.ds)

    def test_validate_time_slot_accepts_half_hour_30_minute_increment(self):
        success, duration = self.service.validate_time_slot(
            future_date(), "09:30", "10:00")

        self.assertTrue(success)
        self.assertEqual(0.5, duration)

    def test_validate_time_slot_rejects_bad_format_and_short_duration(self):
        success, message = self.service.validate_time_slot("bad", "09:00", "10:00")
        self.assertFalse(success)
        self.assertIn("Invalid date", message)

        success, message = self.service.validate_time_slot(
            future_date(), "09:00", "09:15")
        self.assertFalse(success)
        self.assertIn("Minimum booking duration", message)

    def test_validate_time_slot_rejects_non_30_minute_increment(self):
        success, message = self.service.validate_time_slot(
            future_date(), "09:15", "10:15")

        self.assertFalse(success)
        self.assertIn("30-minute increments", message)

    def test_validate_time_slot_rejects_past_start_time(self):
        success, message = self.service.validate_time_slot(
            past_date(), "09:00", "10:00")

        self.assertFalse(success)
        self.assertIn("future", message)

    def test_checkout_rejects_banned_student(self):
        self.student.is_banned = True
        self.student.ban_end_date = future_date(30)

        success, message = self.service.checkout(
            self.student, "rm001", future_date(), "09:00", "11:00", "1")

        self.assertFalse(success)
        self.assertIn("banned", message)

    def test_checkout_with_account_balance_creates_booking_and_transaction(self):
        success, booking = self.service.checkout(
            self.student, "rm001", future_date(), "09:00", "11:00", "1")

        self.assertTrue(success)
        self.assertEqual(Booking.PAYMENT_BALANCE, booking.payment_method)
        self.assertAlmostEqual(180.0, self.student.account_balance)
        self.assertIn(booking.booking_id, self.ds.bookings)
        self.assertTrue(any(t.transaction_type == Transaction.TYPE_BOOKING_PAYMENT
                            for t in self.ds.transactions.values()))

    def test_checkout_rejects_insufficient_funds(self):
        low_balance_student = self.ds.users["stu002"]

        success, message = self.service.checkout(
            low_balance_student, "rm002", future_date(), "09:00", "12:00", "1")

        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)

    def test_checkout_rejects_conflicting_room_time(self):
        add_future_booking(self.ds, self.student, room_id="rm001", days=1,
                           start_time="10:00", end_time="12:00")

        success, message = self.service.checkout(
            self.student, "rm001", future_date(), "11:00", "13:00", "1")

        self.assertFalse(success)
        self.assertIn("no longer available", message)

    def test_checkout_rejects_more_than_three_future_bookings(self):
        for offset in (1, 2, 3):
            add_future_booking(self.ds, self.student, room_id="rm001", days=offset)

        success, message = self.service.checkout(
            self.student, "rm002", future_date(4), "09:00", "10:00", "1")

        self.assertFalse(success)
        self.assertIn("maximum of 3 future bookings", message)

    def test_checkout_applies_newbie20_only_for_first_booking(self):
        new_student = self.ds.users["stu002"]
        new_student.account_balance = 100.0

        success, booking = self.service.checkout(
            new_student, "rm001", future_date(), "09:00", "11:00", "1", "NEWBIE20")

        self.assertTrue(success)
        self.assertAlmostEqual(84.0, new_student.account_balance)
        self.assertEqual(16.0, booking.total_cost)
        self.assertIn(new_student.user_id, self.ds.promo_codes_used)

        success, message = self.service.checkout(
            new_student, "rm001", future_date(2), "09:00", "10:00", "1", "NEWBIE20")
        self.assertFalse(success)
        self.assertIn("already been used", message)

    def test_checkout_with_package_hours_deducts_package(self):
        success, booking = self.service.checkout(
            self.student, "rm001", future_date(), "13:00", "15:00", "2")

        self.assertTrue(success)
        self.assertEqual(Booking.PAYMENT_PACKAGE, booking.payment_method)
        self.assertAlmostEqual(3.0, self.ds.get_package_hours(self.student.user_id))
        self.assertAlmostEqual(200.0, self.student.account_balance)

    def test_checkout_rejects_newbie20_with_package_hours(self):
        success, message = self.service.checkout(
            self.student, "rm001", future_date(), "13:00", "15:00", "2", "NEWBIE20")

        self.assertFalse(success)
        self.assertIn("account balance", message)
        self.assertAlmostEqual(5.0, self.ds.get_package_hours(self.student.user_id))
        self.assertNotIn(self.student.user_id, self.ds.promo_codes_used)

    def test_checkout_rejects_insufficient_package_hours(self):
        self.ds.package_deals.clear()
        self.ds.package_deals["pkg-low"] = PackageDeal(
            package_id="pkg-low",
            student_id=self.student.user_id,
            remaining_hours=1.0,
        )

        success, message = self.service.checkout(
            self.student, "rm001", future_date(), "13:00", "15:00", "2")

        self.assertFalse(success)
        self.assertIn("Insufficient package hours", message)

    def test_checkout_enforces_medium_and_large_room_rules(self):
        success, message = self.service.checkout(
            self.student, "rm002", future_date(), "09:00", "10:00", "1")
        self.assertFalse(success)
        self.assertIn("minimum booking duration", message)

        self.ds.rooms["rm002"].opening_time = "00:00"
        self.ds.rooms["rm002"].closing_time = "23:59"
        self.ds.rooms["rm004"].opening_time = "00:00"
        self.ds.rooms["rm004"].closing_time = "23:59"
        start = datetime.now() + timedelta(hours=2)
        start = start.replace(minute=0 if start.minute < 30 else 30, second=0, microsecond=0)
        end = start + timedelta(hours=2)
        success, message = self.service.checkout(
            self.student,
            "rm002",
            start.strftime("%Y-%m-%d"),
            start.strftime("%H:%M"),
            end.strftime("%H:%M"),
            "1",
        )
        self.assertFalse(success)
        self.assertIn("advance notice", message)

        success, message = self.service.checkout(
            self.student,
            "rm004",
            start.strftime("%Y-%m-%d"),
            start.strftime("%H:%M"),
            end.strftime("%H:%M"),
            "1",
        )
        self.assertFalse(success)
        self.assertIn("advance notice", message)

    def test_checkout_rejects_package_hours_for_non_small_rooms(self):
        starting_hours = self.ds.get_package_hours(self.student.user_id)

        success, message = self.service.checkout(
            self.student, "rm002", future_date(), "09:00", "11:00", "2")

        self.assertFalse(success)
        self.assertIn("Small rooms", message)
        self.assertAlmostEqual(starting_hours, self.ds.get_package_hours(self.student.user_id))

    def test_checkout_rejects_newbie20_for_non_small_rooms_without_saving_usage(self):
        new_student = self.ds.users["stu002"]
        new_student.account_balance = 200.0

        success, message = self.service.checkout(
            new_student, "rm002", future_date(), "09:00", "11:00", "1", "NEWBIE20")

        self.assertFalse(success)
        self.assertIn("Small rooms", message)
        self.assertNotIn(new_student.user_id, self.ds.promo_codes_used)


if __name__ == "__main__":
    unittest.main()
