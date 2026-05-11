from datetime import datetime, timedelta
import unittest

from models.user import Student
from services.auth_service import AuthService
from tests.helpers import build_data_service


class AuthServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.service = AuthService(self.ds)

    def test_login_success_returns_user(self):
        user, message = self.service.login("alice@student.monash.edu", "Password1")

        self.assertIsInstance(user, Student)
        self.assertEqual("Login successful.", message)

    def test_seeded_trello_student_accounts_can_login(self):
        for email in ("student1@student.monash.edu", "student2@student.monash.edu"):
            with self.subTest(email=email):
                user, message = self.service.login(email, "Student123!")

                self.assertIsInstance(user, Student)
                self.assertEqual("Login successful.", message)

    def test_login_fails_for_unknown_email(self):
        user, message = self.service.login("missing@student.monash.edu", "Password1")

        self.assertIsNone(user)
        self.assertIn("Email not found", message)

    def test_login_fails_for_wrong_password(self):
        user, message = self.service.login("alice@student.monash.edu", "wrong")

        self.assertIsNone(user)
        self.assertIn("Incorrect password", message)

    def test_register_success_saves_new_student(self):
        success, result = self.service.register(
            "new@student.monash.edu",
            "ValidPass1",
            "New",
            "Student",
            "30000003",
            "0400000003",
        )

        self.assertTrue(success)
        self.assertIsInstance(result, Student)
        self.assertEqual(result, self.ds.get_student_by_email("new@student.monash.edu"))
        self.assertEqual(1, self.ds.save_count)

    def test_register_collects_validation_errors(self):
        success, message = self.service.register("", "short", "", "", "", "")

        self.assertFalse(success)
        self.assertIn("Email is required.", message)
        self.assertIn("Password must be at least 8 characters long.", message)
        self.assertIn("First name is required.", message)
        self.assertEqual(0, self.ds.save_count)

    def test_register_rejects_duplicate_email(self):
        success, message = self.service.register(
            "alice@student.monash.edu",
            "ValidPass1",
            "Alice",
            "Duplicate",
            "30000004",
            "0400000004",
        )

        self.assertFalse(success)
        self.assertIn("already registered", message)


class StudentPenaltyStateTest(unittest.TestCase):
    def test_add_strike_clears_expired_ban_before_counting_new_violation(self):
        student = Student(
            is_banned=True,
            ban_end_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            late_cancellation_count=2,
            no_show_count=1,
        )

        is_banned = student.add_strike("late_cancellation")

        self.assertFalse(is_banned)
        self.assertFalse(student.is_banned)
        self.assertEqual("", student.ban_end_date)
        self.assertEqual(1, student.late_cancellation_count)
        self.assertEqual(0, student.no_show_count)


if __name__ == "__main__":
    unittest.main()
