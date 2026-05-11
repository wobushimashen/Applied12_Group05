import unittest

from services.room_service import RoomService
from tests.helpers import add_future_booking, build_data_service, future_date


class RoomServiceTest(unittest.TestCase):
    def setUp(self):
        self.ds = build_data_service()
        self.service = RoomService(self.ds)

    def test_browse_rooms_returns_only_available_rooms(self):
        room_ids = {room.room_id for room in self.service.browse_rooms()}

        self.assertIn("rm001", room_ids)
        self.assertIn("rm002", room_ids)
        self.assertNotIn("rm003", room_ids)

    def test_create_room_adds_new_room_and_building_when_needed(self):
        success, room = self.service.create_room("NEW-101", "NEW", room_type="Medium")

        self.assertTrue(success)
        self.assertEqual("NEW-101", room.room_name)
        self.assertEqual("Medium", room.room_type)
        self.assertEqual("3-6", room.capacity_range)
        self.assertEqual(40.0, room.price_per_hour)
        self.assertIn(room.room_id, self.ds.rooms)
        self.assertEqual(1, self.ds.save_count)

    def test_create_room_rejects_duplicate_in_same_building(self):
        success, message = self.service.create_room("LTB-101", "LTB", "2")

        self.assertFalse(success)
        self.assertIn("already exists", message)

    def test_create_room_rejects_invalid_capacity(self):
        for capacity in ("0", "-1", "abc"):
            with self.subTest(capacity=capacity):
                success, _ = self.service.create_room("BAD-101", "LTB", capacity)
                self.assertFalse(success)

    def test_create_room_rejects_blank_room_name(self):
        for room_name in ("", "   "):
            with self.subTest(room_name=room_name):
                self.ds.save_count = 0
                success, message = self.service.create_room(room_name, "LTB")

                self.assertFalse(success)
                self.assertEqual("Room name is required.", message)
                self.assertEqual(0, self.ds.save_count)

    def test_create_room_rejects_blank_building_name(self):
        for building_name in ("", "   "):
            with self.subTest(building_name=building_name):
                self.ds.save_count = 0
                building_count = len(self.ds.buildings)
                success, message = self.service.create_room("NEW-101", building_name)

                self.assertFalse(success)
                self.assertEqual("Building name is required.", message)
                self.assertEqual(building_count, len(self.ds.buildings))
                self.assertEqual(0, self.ds.save_count)

    def test_update_room_changes_details(self):
        success, room = self.service.update_room(
            "rm001",
            new_room_name="LTB-202",
            new_building_name="MTH",
            new_room_type="Medium",
            new_capacity="5",
            new_standard_equipment="Updated equipment",
            new_opening_time="09:00",
            new_closing_time="18:00",
            new_is_available=False,
        )

        self.assertTrue(success)
        self.assertEqual("LTB-202", room.room_name)
        self.assertEqual("bld002", room.building_id)
        self.assertEqual("Medium", room.room_type)
        self.assertEqual(5, room.capacity)
        self.assertEqual("Updated equipment", room.standard_equipment)
        self.assertEqual("09:00", room.opening_time)
        self.assertEqual("18:00", room.closing_time)
        self.assertFalse(room.is_available)

    def test_update_room_rejects_invalid_capacity(self):
        for capacity in ("0", "-1", "abc"):
            with self.subTest(capacity=capacity):
                self.ds.save_count = 0
                success, message = self.service.update_room("rm001", new_capacity=capacity)

                self.assertFalse(success)
                self.assertIn("Capacity", message)
                self.assertEqual(2, self.ds.rooms["rm001"].capacity)
                self.assertEqual(0, self.ds.save_count)

    def test_remove_room_with_future_bookings_marks_unavailable(self):
        student = self.ds.users["stu001"]
        add_future_booking(self.ds, student, room_id="rm001")

        success, message = self.service.remove_room("rm001")

        self.assertTrue(success)
        self.assertIn("marked unavailable", message)
        self.assertIn("rm001", self.ds.rooms)
        self.assertFalse(self.ds.rooms["rm001"].is_available)

    def test_filter_by_time_excludes_conflicting_room(self):
        student = self.ds.users["stu001"]
        date = future_date()
        add_future_booking(self.ds, student, room_id="rm001", days=1,
                           start_time="10:00", end_time="12:00")

        rooms = self.service.filter_by_time(date, "11:00", "13:00")
        room_ids = {room.room_id for room in rooms}

        self.assertNotIn("rm001", room_ids)
        self.assertIn("rm002", room_ids)

    def test_filter_by_time_uses_datetime_not_string_order(self):
        student = self.ds.users["stu001"]
        date = future_date()
        add_future_booking(self.ds, student, room_id="rm001", days=1,
                           start_time="09:00", end_time="11:00")

        rooms = self.service.filter_by_time(date, "9:00", "10:00")
        room_ids = {room.room_id for room in rooms}

        self.assertNotIn("rm001", room_ids)

    def test_filter_by_capacity_returns_matching_range(self):
        rooms = self.service.filter_by_capacity(4, 4)

        self.assertEqual(["rm002"], [room.room_id for room in rooms])

    def test_filter_by_time_excludes_rooms_outside_opening_hours(self):
        self.ds.rooms["rm001"].opening_time = "09:00"
        self.ds.rooms["rm001"].closing_time = "17:00"

        rooms = self.service.filter_by_time(future_date(), "18:00", "19:00")
        room_ids = {room.room_id for room in rooms}

        self.assertNotIn("rm001", room_ids)

    def test_update_room_rejects_invalid_opening_hours_without_saving(self):
        success, message = self.service.update_room("rm001", new_opening_time="bad")

        self.assertFalse(success)
        self.assertIn("Opening and closing times", message)
        self.assertEqual("08:00", self.ds.rooms["rm001"].opening_time)
        self.assertEqual(0, self.ds.save_count)

    def test_get_room_details_includes_equipment_breakdown(self):
        details = self.service.get_room_details("rm001")

        self.assertEqual("LTB", details["building_name"])
        self.assertEqual(2, len(details["all_equipment"]))
        self.assertEqual(["eq001"], [e.equipment_id for e in details["available_equipment"]])
        self.assertEqual(["eq002"], [e.equipment_id for e in details["damaged_equipment"]])

    def test_get_building_names_returns_display_names(self):
        self.assertEqual(["LTB", "MTH"], self.service.get_building_names())


if __name__ == "__main__":
    unittest.main()
