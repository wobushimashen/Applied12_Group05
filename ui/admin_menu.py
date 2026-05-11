from models.user import Admin
from services.room_service import RoomService
from services.booking_service import BookingService


class AdminMenu:
    def __init__(self, data_service):
        self.ds = data_service
        self.room_service = RoomService(data_service)
        self.booking_service = BookingService(data_service)

    def show(self, admin: Admin):
        while True:
            overdue = self.booking_service.get_overdue_bookings()
            print("\n" + "=" * 50)
            print(f"   Admin Dashboard - {admin.first_name} {admin.last_name}")
            print("=" * 50)
            print("  [1] View All Rooms")
            print("  [2] Create Room")
            print("  [3] Update Room")
            print("  [4] Remove Room")
            print("  [5] View All Bookings")
            print("  [6] View All Students")
            print("  [7] Manage Bookings (Mark No-Show)")
            if overdue:
                print(f"  [!] {len(overdue)} overdue booking(s) need review")
            print("  [B] Logout")
            print("-" * 50)
            choice = input(">> Enter your choice: ").strip()

            if choice == "1":
                self._view_all_rooms()
            elif choice == "2":
                self._create_room()
            elif choice == "3":
                self._update_room()
            elif choice == "4":
                self._remove_room()
            elif choice == "5":
                self._view_all_bookings()
            elif choice == "6":
                self._view_all_students()
            elif choice == "7":
                self._manage_bookings()
            elif choice.upper() == "B":
                print("\n[+] Logged out successfully.")
                break
            else:
                print("\n[!] Invalid option. Please try again.")

    def _view_all_rooms(self):
        rooms = self.room_service.get_all_rooms()
        buildings = {b.building_id: b.building_name for b in self.ds.buildings.values()}

        print("\n" + "-" * 50)
        print("   All Rooms")
        print("-" * 50)
        if not rooms:
            print("  No rooms in the system.")
            return

        print(f"  {'Room ID':<10} {'Room Name':<15} {'Type':<8} {'Building':<12} "
              f"{'Capacity':<10} {'Hours':<13} {'Price/hr':<10} {'Available'}")
        print("  " + "-" * 93)
        for room in rooms:
            bname = buildings.get(room.building_id, "Unknown")
            avail = "Yes" if room.is_available else "No"
            print(f"  {room.room_id:<10} {room.room_name:<15} {room.room_type:<8} {bname:<12} "
                  f"{room.capacity_range:<10} {room.opening_time}-{room.closing_time:<5} "
                  f"${room.price_per_hour:<9.2f} {avail}")

    def _create_room(self):
        print("\n" + "-" * 50)
        print("   Create New Room")
        print("-" * 50)
        room_name = input(">> Room Name/Number: ").strip()
        building_name = input(">> Building Name: ").strip()
        room_type = input(">> Room Type (Small/Medium/Large): ").strip()

        success, result = self.room_service.create_room(
            room_name, building_name, room_type=room_type)
        if success:
            room = result
            print(f"\n[+] Room '{room.room_name}' created successfully!")
            print(f"    Building: {building_name}")
            print(f"    Type: {room.room_type}")
            print(f"    Capacity: {room.capacity_range}")
            print(f"    Price: ${room.price_per_hour}/hour")
            print(f"    Standard equipment: {room.standard_equipment}")
        else:
            print(f"\n[!] {result}")

    def _update_room(self):
        self._view_all_rooms()
        print("\n" + "-" * 50)
        print("   Update Room")
        print("-" * 50)
        room_id = input(">> Enter Room ID to update: ").strip()

        room = self.ds.rooms.get(room_id)
        if not room:
            print(f"\n[!] Room not found.")
            return

        print(f"\n  Current: {room.room_name}")
        new_name = input(">> New Room Name (leave blank to keep): ").strip()

        buildings = {b.building_id: b.building_name for b in self.ds.buildings.values()}
        print(f"  Current Building: {buildings.get(room.building_id, 'Unknown')}")
        new_building = input(">> New Building Name (leave blank to keep): ").strip()

        print(f"  Current Capacity: {room.capacity}")
        new_capacity = input(">> New Capacity (leave blank to keep): ").strip()

        print(f"  Current Type: {room.room_type}")
        new_type = input(">> New Type Small/Medium/Large (leave blank to keep): ").strip()

        print(f"  Current Standard Equipment: {room.standard_equipment}")
        new_equipment = input(">> New Standard Equipment (leave blank to keep): ").strip()

        print(f"  Current Opening Hours: {room.opening_time}-{room.closing_time}")
        new_open = input(">> New Opening Time HH:MM (leave blank to keep): ").strip()
        new_close = input(">> New Closing Time HH:MM (leave blank to keep): ").strip()

        print(f"  Current Available: {'Yes' if room.is_available else 'No'}")
        new_avail_str = input(">> Available? (y/n, leave blank to keep): ").strip()
        new_avail = None
        if new_avail_str.lower() == "y":
            new_avail = True
        elif new_avail_str.lower() == "n":
            new_avail = False

        success, result = self.room_service.update_room(
            room_id,
            new_room_name=new_name or None,
            new_building_name=new_building or None,
            new_capacity=new_capacity or None,
            new_is_available=new_avail,
            new_room_type=new_type or None,
            new_standard_equipment=new_equipment or None,
            new_opening_time=new_open or None,
            new_closing_time=new_close or None,
        )
        if success:
            room = result
            print(f"\n[+] Room updated successfully!")
            print(f"    Name: {room.room_name}")
            print(f"    Type: {room.room_type}")
            print(f"    Capacity: {room.capacity_range}")
            print(f"    Opening Hours: {room.opening_time}-{room.closing_time}")
            print(f"    Available: {'Yes' if room.is_available else 'No'}")
        else:
            print(f"\n[!] {result}")

    def _remove_room(self):
        self._view_all_rooms()
        print("\n" + "-" * 50)
        print("   Remove Room")
        print("-" * 50)
        room_id = input(">> Enter Room ID to remove: ").strip()

        confirm = input(f">> Are you sure you want to remove this room? (y/n): ").strip()
        if confirm.lower() != "y":
            print("\n[*] Removal cancelled.")
            return

        success, message = self.room_service.remove_room(room_id)
        if success:
            print(f"\n[+] {message}")
        else:
            print(f"\n[!] {message}")

    def _view_all_bookings(self):
        bookings = list(self.ds.bookings.values())
        print("\n" + "-" * 70)
        print("   All Bookings")
        print("-" * 70)
        if not bookings:
            print("  No bookings in the system.")
            return

        print(f"  {'Reference':<18} {'Student':<12} {'Room':<10} {'Date':<12} {'Time':<14} {'Status'}")
        print("  " + "-" * 70)
        for b in bookings:
            student = self.ds.users.get(b.student_id)
            sname = student.first_name if student else "Unknown"
            room = self.ds.rooms.get(b.room_id)
            rname = room.room_name if room else "Unknown"
            print(f"  {b.booking_reference:<18} {sname:<12} {rname:<10} {b.date:<12} "
                  f"{b.start_time}-{b.end_time:<6} {b.status}")

    def _view_all_students(self):
        students = [u for u in self.ds.users.values() if hasattr(u, "student_id")]
        print("\n" + "-" * 70)
        print("   All Students")
        print("-" * 70)
        if not students:
            print("  No students registered.")
            return

        print(f"  {'ID':<10} {'Name':<20} {'Email':<30} {'Balance':<10} {'Strikes':<8} {'Banned'}")
        print("  " + "-" * 75)
        for s in students:
            banned = "Yes" if s.is_banned else "No"
            strikes = s.late_cancellation_count + s.no_show_count
            print(f"  {s.student_id:<10} {s.first_name} {s.last_name:<14} {s.email:<30} "
                  f"${s.account_balance:<9.2f} {strikes}/3{'':<4} {banned}")

    def _manage_bookings(self):
        """Admin can review overdue bookings and mark no-shows."""
        overdue = self.booking_service.get_overdue_bookings()

        print("\n" + "-" * 60)
        print("   Manage Bookings - Mark No-Show")
        print("-" * 60)

        if not overdue:
            print("  No overdue bookings to review.")
            return

        buildings = {b.building_id: b.building_name for b in self.ds.buildings.values()}
        print(f"  {'#':<4} {'Reference':<18} {'Student':<12} {'Room':<10} {'Date':<12} {'Time'}")
        print("  " + "-" * 60)
        for i, b in enumerate(overdue, 1):
            student = self.ds.users.get(b.student_id)
            sname = student.first_name if student else "Unknown"
            room = self.ds.rooms.get(b.room_id)
            rname = room.room_name if room else "Unknown"
            print(f"  [{i}]  {b.booking_reference:<18} {sname:<12} {rname:<10} {b.date:<12} "
                  f"{b.start_time}-{b.end_time}")

        print("\n  [A] Mark ALL as No-Show")
        print("  [S] Select individual booking")
        print("  [B] Go back")
        choice = input(">> Enter choice: ").strip()

        if choice.upper() == "B":
            return
        elif choice.upper() == "A":
            for b in overdue:
                ok, msg = self.booking_service.mark_no_show_admin(b.booking_id)
                if ok:
                    print(f"\n[+] {msg}")
        elif choice.upper() == "S":
            try:
                sel = int(input(">> Select booking (#): ").strip())
                if sel < 1 or sel > len(overdue):
                    print("\n[!] Invalid selection.")
                    return
            except ValueError:
                print("\n[!] Invalid input.")
                return

            booking = overdue[sel - 1]
            student = self.ds.users.get(booking.student_id)
            sname = f"{student.first_name} {student.last_name}" if student else "Unknown"

            confirm = input(f">> Mark {booking.booking_reference} ({sname}) as No-Show? (y/n): ").strip()
            if confirm.lower() != "y":
                print("\n[*] Cancelled.")
                return

            ok, msg = self.booking_service.mark_no_show_admin(booking.booking_id)
            if ok:
                print(f"\n[+] {msg}")
            else:
                print(f"\n[!] {msg}")
