import tempfile
import unittest
from unittest.mock import patch

from services.data_service import DataService


class DataServiceTest(unittest.TestCase):
    def test_initializes_mock_data_when_csv_files_are_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("services.data_service.DATA_DIR", temp_dir):
                ds = DataService()

                self.assertGreaterEqual(len(ds.users), 2)
                self.assertGreaterEqual(len(ds.rooms), 1)
                self.assertGreaterEqual(len(ds.bookings), 1)
                self.assertIsNotNone(ds.get_user_by_email("admin@monash.edu"))
                self.assertIsNotNone(ds.get_user_by_email("student1@student.monash.edu"))
                self.assertIsNotNone(ds.get_user_by_email("student2@student.monash.edu"))
                self.assertEqual("Student123!",
                                 ds.get_user_by_email("student1@student.monash.edu").password)
                self.assertEqual(80.0, ds.bookings["bk002"].total_cost)
                self.assertEqual(160.0, ds.bookings["bk013"].total_cost)
                self.assertEqual("Small", ds.rooms[ds.bookings["bk006"].room_id].room_type)
                self.assertEqual("Small", ds.rooms[ds.bookings["bk007"].room_id].room_type)
                self.assertEqual(80.0, ds.transactions["tx006"].amount)
                self.assertEqual(160.0, ds.transactions["tx018"].amount)
                self.assertEqual(120.0, ds.transactions["tx024"].amount)

    def test_save_and_reload_round_trip_preserves_core_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("services.data_service.DATA_DIR", temp_dir):
                ds = DataService()
                student = ds.get_student_by_email("alice@student.monash.edu")
                student.account_balance += 12.5
                ds.save_all()

                reloaded = DataService()
                reloaded_student = reloaded.get_student_by_email("alice@student.monash.edu")

                self.assertIsNotNone(reloaded_student)
                self.assertAlmostEqual(student.account_balance,
                                       reloaded_student.account_balance)
                self.assertEqual(len(ds.rooms), len(reloaded.rooms))
                self.assertEqual("Small", reloaded.rooms["rm001"].room_type)
                self.assertEqual("Medium", reloaded.rooms["rm004"].room_type)
                self.assertEqual("Large", reloaded.rooms["rm008"].room_type)
                self.assertEqual("1 table, 2 chairs",
                                 reloaded.rooms["rm001"].standard_equipment)

    def test_helper_methods_calculate_and_mutate_package_hours(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("services.data_service.DATA_DIR", temp_dir):
                ds = DataService()
                student = ds.get_student_by_email("charlie@student.monash.edu")
                starting_hours = ds.get_package_hours(student.user_id)

                self.assertGreater(starting_hours, 0)
                self.assertTrue(ds.deduct_package_hours(student.user_id, 2.0))
                self.assertAlmostEqual(starting_hours - 2.0,
                                       ds.get_package_hours(student.user_id))

                ds.restore_package_hours(student.user_id, 1.5)
                self.assertAlmostEqual(starting_hours - 0.5,
                                       ds.get_package_hours(student.user_id))

    def test_csv_read_failure_returns_empty_rows_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("services.data_service.DATA_DIR", temp_dir):
                ds = DataService()
                with patch("builtins.open", side_effect=OSError("read denied")), \
                        patch("builtins.print"):
                    self.assertEqual([], ds._read_csv("users.csv"))

    def test_csv_write_failure_does_not_crash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("services.data_service.DATA_DIR", temp_dir):
                ds = DataService()
                with patch("builtins.open", side_effect=OSError("write denied")), \
                        patch("builtins.print"):
                    ds._write_csv("users.csv", ["user_id"], [{"user_id": "u1"}])


if __name__ == "__main__":
    unittest.main()
