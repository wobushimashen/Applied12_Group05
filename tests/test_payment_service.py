import unittest

from models.transaction import Transaction
from services.payment_service import PaymentService
from tests.helpers import build_data_service


class PaymentServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.student = self.ds.users["stu001"]
        self.service = PaymentService(self.ds)

    def test_add_funds_accepts_positive_amount(self):
        success, message = self.service.add_funds(self.student, "50.25")

        self.assertTrue(success)
        self.assertAlmostEqual(250.25, self.student.account_balance)
        self.assertIn("New balance: $250.25", message)
        self.assertTrue(any(t.transaction_type == Transaction.TYPE_TOPUP
                            for t in self.ds.transactions.values()))
        self.assertEqual(1, self.ds.save_count)

    def test_add_funds_rejects_non_number(self):
        success, message = self.service.add_funds(self.student, "abc")

        self.assertFalse(success)
        self.assertIn("valid positive amount", message)
        self.assertAlmostEqual(200.0, self.student.account_balance)
        self.assertEqual(0, self.ds.save_count)

    def test_add_funds_rejects_zero_and_negative_amounts(self):
        for amount in ("0", "0.001", "-1"):
            with self.subTest(amount=amount):
                success, _ = self.service.add_funds(self.student, amount)
                self.assertFalse(success)

        self.assertAlmostEqual(200.0, self.student.account_balance)

    def test_add_funds_rejects_nan_and_infinity(self):
        for amount in ("nan", "inf"):
            with self.subTest(amount=amount):
                success, _ = self.service.add_funds(self.student, amount)
                self.assertFalse(success)

        self.assertAlmostEqual(200.0, self.student.account_balance)

    def test_add_funds_rejects_amount_above_limit(self):
        success, message = self.service.add_funds(self.student, "1000.01")

        self.assertFalse(success)
        self.assertIn("Maximum top-up amount", message)

    def test_purchase_package_deal_deducts_balance_and_adds_hours(self):
        success, message = self.service.purchase_package_deal(self.student)

        self.assertTrue(success)
        self.assertAlmostEqual(100.0, self.student.account_balance)
        self.assertAlmostEqual(17.0, self.ds.get_package_hours(self.student.user_id))
        self.assertIn("Package Deal purchased", message)
        self.assertTrue(any(t.transaction_type == Transaction.TYPE_PACKAGE_PURCHASE
                            for t in self.ds.transactions.values()))

    def test_purchase_package_deal_rejects_insufficient_balance(self):
        low_balance_student = self.ds.users["stu002"]

        success, message = self.service.purchase_package_deal(low_balance_student)

        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)
        self.assertAlmostEqual(25.0, low_balance_student.account_balance)

    def test_get_transaction_history_filters_by_student(self):
        self.service.add_funds(self.student, "10")
        self.service.add_funds(self.ds.users["stu002"], "20")

        history = self.service.get_transaction_history(self.student.user_id)

        self.assertEqual(1, len(history))
        self.assertEqual(self.student.user_id, history[0].student_id)


if __name__ == "__main__":
    unittest.main()
