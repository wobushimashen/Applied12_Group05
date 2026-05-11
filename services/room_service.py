from datetime import datetime

from models.room import Room


class RoomService:
    def __init__(self, data_service):
        self.ds = data_service

    # ── Admin Operations ────────────────────────────────────
    def create_room(self, room_name, building_name, capacity=None, room_type=None):
        room_name = room_name.strip() if room_name else ""
        building_name = building_name.strip() if building_name else ""
        if not room_name:
            return False, "Room name is required."
        if not building_name:
            return False, "Building name is required."

        building = self.ds.get_building_by_name(building_name)
        if not building:
            from models.building import Building
            building = Building(building_name=building_name)
            self.ds.buildings[building.building_id] = building

        if self.ds.room_exists_in_building(room_name, building.building_id):
            return False, "A room with this name already exists in this building."

        normalized_type = Room.normalize_room_type(room_type)
        if room_type and not normalized_type:
            return False, "Room type must be Small, Medium, or Large."

        if capacity not in (None, ""):
            try:
                capacity = int(capacity)
                if capacity <= 0:
                    return False, "Capacity must be a positive integer."
            except ValueError:
                return False, "Capacity must be a valid number."
        elif normalized_type:
            capacity = Room.TYPE_DEFAULTS[normalized_type]["capacity_max"]
        else:
            capacity = Room.TYPE_DEFAULTS[Room.TYPE_SMALL]["capacity_max"]

        room = Room(
            room_name=room_name,
            building_id=building.building_id,
            room_type=room_type,
            capacity=capacity,
            room_type=normalized_type,
        )
        self.ds.rooms[room.room_id] = room
        self.ds.save_all()
        return True, room

    def update_room(self, room_id, new_room_name=None, new_building_name=None,
                    new_capacity=None, new_is_available=None,
                    new_room_type=None, new_standard_equipment=None,
                    new_opening_time=None, new_closing_time=None):
        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."

        normalized_type = None
        if new_room_type is not None and new_room_type != "":
            normalized_type = Room.normalize_room_type(new_room_type)
            if not normalized_type:
                return False, "Room type must be Small, Medium, or Large."

        cap = None
        if new_capacity is not None:
            try:
                cap = int(new_capacity)
            except ValueError:
                return False, "Capacity must be a valid number."
            if cap <= 0:
                return False, "Capacity must be a positive integer."

        opening_time = new_opening_time if new_opening_time not in (None, "") else room.opening_time
        closing_time = new_closing_time if new_closing_time not in (None, "") else room.closing_time
        if not self._valid_opening_window(opening_time, closing_time):
            return False, "Opening and closing times must use HH:MM format and closing time must be after opening time."

        if new_room_name and new_room_name.strip():
            room.room_name = new_room_name.strip()

        if new_building_name and new_building_name.strip():
            building = self.ds.get_building_by_name(new_building_name.strip())
            if not building:
                from models.building import Building
                building = Building(building_name=new_building_name.strip())
                self.ds.buildings[building.building_id] = building
            room.building_id = building.building_id

        if normalized_type:
            defaults = Room.TYPE_DEFAULTS[normalized_type]
            room.room_type = normalized_type
            room.capacity_min = defaults["capacity_min"]
            room.capacity_max = defaults["capacity_max"]
            room.capacity = defaults["capacity_max"]
            room.price_per_hour = defaults["price_per_hour"]
            room.standard_equipment = defaults["standard_equipment"]
            room.minimum_duration = defaults["minimum_duration"]
            room.advance_notice_hours = defaults["advance_notice_hours"]
            room.late_cancellation_refund_rate = defaults["late_cancellation_refund_rate"]
            room.no_show_refund_rate = defaults["no_show_refund_rate"]

        if cap is not None:
            if cap < room.capacity_min or cap > room.capacity_max:
                return False, f"Capacity for {room.room_type} rooms must be between {room.capacity_min} and {room.capacity_max}."
            room.capacity = cap

        if new_standard_equipment is not None and new_standard_equipment.strip():
            room.standard_equipment = new_standard_equipment.strip()

        room.opening_time = opening_time
        room.closing_time = closing_time

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
            return True, "Room has active or future bookings, so it was marked unavailable instead of deleted."

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
            if (self.room_is_open_for_slot(room, date, start_time, end_time)
                    and not self.ds.check_room_conflict(room.room_id, date, start_time, end_time)):
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
        return [b.building_name for b in self.ds.buildings.values()]

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
        try:
            min_capacity = int(min_capacity)
            max_capacity = int(max_capacity)
        except (TypeError, ValueError):
            return []
        return [
            r for r in rooms
            if r.capacity_min <= max_capacity and r.capacity_max >= min_capacity
        ]

    def room_is_open_for_slot(self, room, date, start_time, end_time):
        try:
            requested_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            requested_end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            opening = datetime.strptime(f"{date} {room.opening_time}", "%Y-%m-%d %H:%M")
            closing = datetime.strptime(f"{date} {room.closing_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return False
        return opening <= requested_start and requested_end <= closing

    def _valid_opening_window(self, opening_time, closing_time):
        try:
            opening = datetime.strptime(opening_time, "%H:%M")
            closing = datetime.strptime(closing_time, "%H:%M")
        except ValueError:
            return False
        return closing > opening
