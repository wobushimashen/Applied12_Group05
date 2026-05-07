from datetime import datetime

from models.room import Room


class RoomService:
    def __init__(self, data_service):
        self.ds = data_service

    def create_room(self, room_name, building_name, capacity=None, room_type="Small"):
        building = self.ds.get_building_by_name(building_name)
        if not building:
            from models.building import Building
            building = Building(building_name=building_name)
            self.ds.buildings[building.building_id] = building

        if self.ds.room_exists_in_building(room_name, building.building_id):
            return False, "A room with this name already exists in this building."

        room_type = Room.normalize_room_type(room_type, capacity or 2)
        defaults = Room.defaults_for_type(room_type)
        if capacity in (None, ""):
            capacity = defaults["capacity"]
        try:
            capacity = int(capacity)
            if capacity <= 0:
                return False, "Capacity must be a positive integer."
        except ValueError:
            return False, "Capacity must be a valid number."

        room = Room(
            room_name=room_name,
            building_id=building.building_id,
            room_type=room_type,
            capacity=capacity,
            standard_equipment=defaults["standard_equipment"],
            price_per_hour=defaults["price_per_hour"],
        )
        self.ds.rooms[room.room_id] = room
        self.ds.save_all()
        return True, room

    def update_room(self, room_id, new_room_name=None, new_building_name=None,
                    new_capacity=None, new_is_available=None,
                    new_standard_equipment=None, new_opening_time=None,
                    new_closing_time=None):
        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."

        if new_room_name and new_room_name.strip():
            room.room_name = new_room_name.strip()

        if new_building_name and new_building_name.strip():
            building = self.ds.get_building_by_name(new_building_name.strip())
            if not building:
                from models.building import Building
                building = Building(building_name=new_building_name.strip())
                self.ds.buildings[building.building_id] = building
            room.building_id = building.building_id

        if new_capacity is not None and str(new_capacity).strip():
            try:
                cap = int(new_capacity)
                if cap > 0:
                    room.capacity = cap
            except ValueError:
                return False, "Capacity must be a valid number."

        if new_standard_equipment and new_standard_equipment.strip():
            room.standard_equipment = new_standard_equipment.strip()

        if new_opening_time and new_opening_time.strip():
            if not self._valid_time(new_opening_time.strip()):
                return False, "Opening time must use HH:MM format."
            room.opening_time = new_opening_time.strip()

        if new_closing_time and new_closing_time.strip():
            if not self._valid_time(new_closing_time.strip()):
                return False, "Closing time must use HH:MM format."
            room.closing_time = new_closing_time.strip()

        if new_is_available is not None:
            room.is_available = new_is_available

        self.ds.save_all()
        return True, room

    def remove_room(self, room_id):
        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."

        if self.ds.has_room_future_bookings(room_id):
            room.is_available = False
            self.ds.save_all()
            return True, "Room has future active bookings, so it was marked unavailable instead of deleted."

        eq_to_remove = [eid for eid, e in self.ds.equipment.items()
                        if e.room_id == room_id]
        for eid in eq_to_remove:
            del self.ds.equipment[eid]

        del self.ds.rooms[room_id]
        self.ds.save_all()
        return True, "Room removed successfully."

    def get_all_rooms(self):
        return list(self.ds.rooms.values())

    def browse_rooms(self):
        return [r for r in self.ds.rooms.values() if r.is_available]

    def filter_by_time(self, date, start_time, end_time, rooms=None):
        if rooms is None:
            rooms = self.browse_rooms()
        available = []
        for room in rooms:
            if not self._within_opening_hours(room, start_time, end_time):
                continue
            if not self.ds.check_room_conflict(room.room_id, date, start_time, end_time):
                available.append(room)
        return available

    def filter_by_building(self, building_name, rooms=None):
        if rooms is None:
            rooms = self.browse_rooms()
        building = self.ds.get_building_by_name(building_name)
        if not building:
            return []
        return [r for r in rooms if r.building_id == building.building_id]

    def get_building_names(self):
        return list(self.ds.buildings.keys())

    def get_all_building_names(self):
        return [b.building_name for b in self.ds.buildings.values()]

    def get_room_by_id(self, room_id):
        return self.ds.rooms.get(room_id)

    def get_room_details(self, room_id):
        room = self.ds.rooms.get(room_id)
        if not room:
            return None

        building = self.ds.buildings.get(room.building_id)
        building_name = building.building_name if building else "Unknown"

        equipment = self.ds.get_equipment_by_room(room_id)
        available_eq = [e for e in equipment if e.is_available and not e.is_damaged]
        damaged_eq = [e for e in equipment if e.is_damaged]

        return {
            "room": room,
            "building_name": building_name,
            "all_equipment": equipment,
            "available_equipment": available_eq,
            "damaged_equipment": damaged_eq,
        }

    def filter_by_capacity(self, min_capacity, max_capacity, rooms=None):
        if rooms is None:
            rooms = self.browse_rooms()
        return [r for r in rooms
                if r.min_capacity <= max_capacity and min_capacity <= r.max_capacity]

    def _valid_time(self, value):
        try:
            datetime.strptime(value, "%H:%M")
            return True
        except ValueError:
            return False

    def _within_opening_hours(self, room, start_time, end_time):
        return room.opening_time <= start_time and end_time <= room.closing_time

