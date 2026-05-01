from models.room import Room


class RoomService:
    def __init__(self, data_service):
        self.ds = data_service

    # ── Admin Operations ────────────────────────────────────
    def create_room(self, room_name, building_name, capacity):
        building = self.ds.get_building_by_name(building_name)
        if not building:
            # Auto-create building
            from models.building import Building
            building = Building(building_name=building_name)
            self.ds.buildings[building.building_id] = building

        if self.ds.room_exists_in_building(room_name, building.building_id):
            return False, "A room with this name already exists in this building."

        try:
            capacity = int(capacity)
            if capacity <= 0:
                return False, "Capacity must be a positive integer."
        except ValueError:
            return False, "Capacity must be a valid number."

        room = Room(
            room_name=room_name,
            building_id=building.building_id,
            capacity=capacity,
            price_per_hour=10.0,
        )
        self.ds.rooms[room.room_id] = room
        self.ds.save_all()
        return True, room

    def update_room(self, room_id, new_room_name=None, new_building_name=None,
                    new_capacity=None, new_is_available=None):
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

        if new_capacity is not None:
            try:
                cap = int(new_capacity)
                if cap > 0:
                    room.capacity = cap
            except ValueError:
                pass

        if new_is_available is not None:
            room.is_available = new_is_available

        self.ds.save_all()
        return True, room

    def remove_room(self, room_id):
        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."

        if self.ds.has_room_future_bookings(room_id):
            return False, "Cannot remove a room with future active bookings."

        # Remove equipment associated with this room
        eq_to_remove = [eid for eid, e in self.ds.equipment.items()
                        if e.room_id == room_id]
        for eid in eq_to_remove:
            del self.ds.equipment[eid]

        del self.ds.rooms[room_id]
        self.ds.save_all()
        return True, "Room removed successfully."

    def get_all_rooms(self):
        return list(self.ds.rooms.values())

    # ── Student Operations ──────────────────────────────────
    def browse_rooms(self):
        return [r for r in self.ds.rooms.values() if r.is_available]

    def filter_by_time(self, date, start_time, end_time, rooms=None):
        if rooms is None:
            rooms = self.browse_rooms()
        available = []
        for room in rooms:
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
