from models.user import Student
from services.room_service import RoomService
from services.booking_service import BookingService
from services.equipment_service import EquipmentService
from services.payment_service import PaymentService


class StudentMenu:
    def __init__(self, data_service):
        self.ds = data_service
        self.room_service = RoomService(data_service)
        self.booking_service = BookingService(data_service)
        self.equipment_service = EquipmentService(data_service)
        self.payment_service = PaymentService(data_service)

    def show(self, student: Student):
        while True:
            package_hours = self.ds.get_package_hours(student.user_id)
            active_count = len(self.ds.get_active_future_bookings(student.user_id))

            print("\n" + "=" * 50)
            print(f"   Student Dashboard - {student.first_name} {student.last_name}")
            print("=" * 50)
            print(f"  Balance: ${student.account_balance:.2f}  |  "
                  f"Package Hours: {package_hours:.1f}  |  "
                  f"Active Bookings: {active_count}/3")
            if student.is_banned:
                print(f"  [!] BANNED until {student.ban_end_date}")
            print("-" * 50)
            print("  [1] Browse Available Rooms")
            print("  [2] My Bookings")
            print("  [3] Cancel a Booking")
            print("  [4] Add Funds")
            print("  [5] Purchase Package Deal")
            print("  [6] My Profile")
            print("  [7] Transaction History")
            print("  [8] Borrow Equipment (during active session)")
            print("  [9] Return Equipment")
            print("  [B] Logout")
            print("-" * 50)
            choice = input(">> Enter your choice: ").strip()

            if choice == "1":
                self._browse_and_book(student)
            elif choice == "2":
                self._my_bookings(student)
            elif choice == "3":
                self._cancel_booking(student)
            elif choice == "4":
                self._add_funds(student)
            elif choice == "5":
                self._purchase_package(student)
            elif choice == "6":
                self._my_profile(student)
            elif choice == "7":
                self._transaction_history(student)
            elif choice == "8":
                self._borrow_equipment(student)
            elif choice == "9":
                self._return_equipment(student)
            elif choice.upper() == "B":
                print("\n[+] Logged out successfully.")
                break
            else:
                print("\n[!] Invalid option. Please try again.")

    # ── Browse and Book ─────────────────────────────────────
    def _browse_and_book(self, student: Student):
        # Check if banned
        if not student.can_make_booking():
            print(f"\n[!] You are currently banned from booking until {student.ban_end_date} "
                  f"due to repeated late cancellations or no-shows.")
            return

        # Check max bookings
        active = self.ds.get_active_future_bookings(student.user_id)
        if len(active) >= 3:
            print("\n[!] You have reached the maximum of 3 future bookings. "
                  "Please cancel an existing booking first.")
            return

        print("\n" + "-" * 50)
        print("   Browse Available Rooms")
        print("-" * 50)

        # Get all available rooms
        rooms = self.room_service.browse_rooms()
        buildings = {b.building_id: b.building_name for b in self.ds.buildings.values()}

        if not rooms:
            print("  No rooms available.")
            return

        # Display all rooms
        print(f"\n  {'#':<4} {'Room':<15} {'Building':<12} {'Capacity':<10} {'Price/hr'}")
        print("  " + "-" * 50)
        for i, room in enumerate(rooms, 1):
            bname = buildings.get(room.building_id, "Unknown")
            print(f"  [{i}]  {room.room_name:<15} {bname:<12} {room.capacity:<10} ${room.price_per_hour:.2f}")

        # Time filter
        print("\n  Filter by time (or press Enter to skip):")
        date = input("  >> Date (YYYY-MM-DD): ").strip()
        if date:
            start_time = input("  >> Start Time (HH:MM): ").strip()
            end_time = input("  >> End Time (HH:MM): ").strip()

            valid, msg = self.booking_service.validate_time_slot(date, start_time, end_time)
            if not valid:
                print(f"\n[!] {msg}")
                return

            rooms = self.room_service.filter_by_time(date, start_time, end_time, rooms)
            if not rooms:
                print("\n[!] No rooms available for the selected criteria. Please adjust your filters.")
                return

            print(f"\n  Available rooms for {date} {start_time}-{end_time}:")
            print(f"  {'#':<4} {'Room':<15} {'Building':<12} {'Capacity':<10} {'Price/hr'}")
            print("  " + "-" * 50)
            for i, room in enumerate(rooms, 1):
                bname = buildings.get(room.building_id, "Unknown")
                print(f"  [{i}]  {room.room_name:<15} {bname:<12} {room.capacity:<10} ${room.price_per_hour:.2f}")

        # Building filter
        all_building_names = self.room_service.get_all_building_names()
        print(f"\n  Available buildings: {', '.join(all_building_names)}")
        building_filter = input("  >> Filter by building (or press Enter to skip): ").strip()
        if building_filter:
            rooms = self.room_service.filter_by_building(building_filter, rooms)
            if not rooms:
                print("\n[!] No rooms available for the selected criteria. Please adjust your filters.")
                return

            print(f"\n  Rooms in {building_filter}:")
            print(f"  {'#':<4} {'Room':<15} {'Capacity':<10} {'Price/hr'}")
            print("  " + "-" * 40)
            for i, room in enumerate(rooms, 1):
                print(f"  [{i}]  {room.room_name:<15} {room.capacity:<10} ${room.price_per_hour:.2f}")

        # Select room
        print("\n  Select a room to view details or book:")
        try:
            sel = int(input("  >> Room number (#): ").strip())
            if sel < 1 or sel > len(rooms):
                print("\n[!] Invalid selection.")
                return
        except ValueError:
            print("\n[!] Invalid input.")
            return

        selected_room = rooms[sel - 1]

        # Show room details before booking
        self._show_room_details(selected_room.room_id)

        # If no date/time entered yet, get it now
        if not date:
            date = input("  >> Date (YYYY-MM-DD): ").strip()
            start_time = input("  >> Start Time (HH:MM): ").strip()
            end_time = input("  >> End Time (HH:MM): ").strip()

            valid, msg = self.booking_service.validate_time_slot(date, start_time, end_time)
            if not valid:
                print(f"\n[!] {msg}")
                return

            if self.ds.check_room_conflict(selected_room.room_id, date, start_time, end_time):
                print("\n[!] This room is no longer available for the selected time.")
                return

        # Checkout summary
        from datetime import datetime
        start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        duration = (end - start).total_seconds() / 3600
        total_cost = duration * selected_room.price_per_hour

        bname = buildings.get(selected_room.building_id, "Unknown")
        print("\n" + "-" * 50)
        print("   Checkout Summary")
        print("-" * 50)
        print(f"  Room:      {selected_room.room_name} ({bname})")
        print(f"  Date:      {date}")
        print(f"  Time:      {start_time} - {end_time}")
        print(f"  Duration:  {duration:.1f} hour(s)")
        print(f"  Cost:      ${total_cost:.2f}")
        print(f"  Equipment: Table and Chair included")
        print("-" * 50)
        print(f"  [1] Pay with Account Balance (${student.account_balance:.2f})")
        package_hours = self.ds.get_package_hours(student.user_id)
        print(f"  [2] Pay with Package Hours ({package_hours:.1f} hours)")
        print(f"  [B] Cancel")
        print("-" * 50)

        pay_choice = input(">> Select payment method: ").strip()

        if pay_choice.upper() == "B":
            print("\n[*] Checkout cancelled.")
            return

        # Ask for promo code
        promo = input(">> Promo code (or press Enter to skip): ").strip()

        success, result = self.booking_service.checkout(
            student, selected_room.room_id, date, start_time, end_time,
            pay_choice, promo if promo else None
        )

        if success:
            booking = result
            print(f"\n[+] Booking confirmed!")
            print(f"    Reference: {booking.booking_reference}")
            print(f"    Room: {selected_room.room_name}")
            print(f"    Date: {date}")
            print(f"    Time: {start_time} - {end_time}")
            print(f"    Remaining balance: ${student.account_balance:.2f}")
        else:
            print(f"\n[!] {result}")

    # ── My Bookings ─────────────────────────────────────────
    def _my_bookings(self, student: Student):
        bookings = self.booking_service.get_student_bookings(student.user_id)
        buildings = {b.building_id: b.building_name for b in self.ds.buildings.values()}

        print("\n" + "-" * 75)
        print(f"   My Bookings  |  Late Cancellations: {student.late_cancellation_count}  "
              f"|  No-Shows: {student.no_show_count}")
        total_strikes = student.late_cancellation_count + student.no_show_count
        if total_strikes > 0:
            print(f"   [!] Warning: {total_strikes}/3 strikes. 3 strikes = 3-month ban.")
        print("-" * 75)

        if not bookings:
            print("  You have no bookings.")
            return

        print(f"  {'#':<4} {'Reference':<18} {'Room':<10} {'Building':<10} {'Date':<12} "
              f"{'Time':<14} {'Cost':<10} {'Status'}")
        print("  " + "-" * 75)
        for i, b in enumerate(bookings, 1):
            room = self.ds.rooms.get(b.room_id)
            rname = room.room_name if room else "Unknown"
            bname = buildings.get(room.building_id, "Unknown") if room else "Unknown"
            cost = f"${b.total_cost:.2f}" if b.payment_method == "AccountBalance" else f"{b.duration:.1f}hrs"
            print(f"  [{i}]  {b.booking_reference:<18} {rname:<10} {bname:<10} {b.date:<12} "
                  f"{b.start_time}-{b.end_time:<6} {cost:<10} {b.status}")

    # ── Cancel Booking ──────────────────────────────────────
    def _cancel_booking(self, student: Student):
        active_bookings = self.booking_service.get_active_future_bookings(student.user_id)

        if not active_bookings:
            print("\n[!] You have no active bookings to cancel.")
            return

        # Display strike count and ban warning
        total_strikes = student.late_cancellation_count + student.no_show_count
        print("\n" + "-" * 60)
        print("   Cancel a Booking")
        print("-" * 60)
        if total_strikes > 0:
            print(f"  [!] Warning: {total_strikes}/3 strikes. 3 strikes = 3-month ban.")
        if student.is_banned:
            print(f"  [!] BANNED until {student.ban_end_date}")
        print(f"  {'#':<4} {'Reference':<18} {'Room':<10} {'Date':<12} {'Time'}")
        print("  " + "-" * 60)
        for i, b in enumerate(active_bookings, 1):
            room = self.ds.rooms.get(b.room_id)
            rname = room.room_name if room else "Unknown"
            print(f"  [{i}]  {b.booking_reference:<18} {rname:<10} {b.date:<12} "
                  f"{b.start_time}-{b.end_time}")

        try:
            sel = int(input("\n>> Select booking to cancel (#): ").strip())
            if sel < 1 or sel > len(active_bookings):
                print("\n[!] Invalid selection.")
                return
        except ValueError:
            print("\n[!] Invalid input.")
            return

        booking = active_bookings[sel - 1]

        # Show cancellation type and refund details before confirmation
        cancel_type = self.booking_service.get_cancellation_type(booking)
        room = self.ds.rooms.get(booking.room_id)
        rname = room.room_name if room else "Unknown"

        print(f"\n  Booking:    {booking.booking_reference}")
        print(f"  Room:       {rname}")
        print(f"  Date/Time:  {booking.date} {booking.start_time}-{booking.end_time}")
        print(f"  Type:       {cancel_type}")
        if cancel_type == "Late Cancellation":
            print(f"  [!] This will be recorded as a Late Cancellation strike.")
        if booking.payment_method == "PackageHours":
            print(f"  Refund:     {booking.duration:.1f} package hours will be restored")
        else:
            print(f"  Refund:     ${booking.original_cost:.2f} (full refund to account balance)")

        confirm = input(f"\n>> Confirm cancellation? (y/n): ").strip()
        if confirm.lower() != "y":
            print("\n[*] Cancellation aborted.")
            return

        success, message = self.booking_service.cancel_booking(student, booking.booking_id)
        if success:
            print(f"\n[+] {message}")
        else:
            print(f"\n[!] {message}")

    # ── Add Funds ───────────────────────────────────────────
    def _add_funds(self, student: Student):
        print("\n" + "-" * 50)
        print(f"   Add Funds  |  Current Balance: ${student.account_balance:.2f}")
        print("-" * 50)
        amount = input(">> Enter amount to add ($0.01 - $1000.00): ").strip()

        success, message = self.payment_service.add_funds(student, amount)
        if success:
            print(f"\n[+] {message}")
        else:
            print(f"\n[!] {message}")

    # ── Purchase Package ────────────────────────────────────
    def _purchase_package(self, student: Student):
        package_hours = self.ds.get_package_hours(student.user_id)
        print("\n" + "-" * 50)
        print("   Package Deal")
        print("-" * 50)
        print(f"  Price:        $100.00 AUD")
        print(f"  Hours:        12 bookable hours")
        print(f"  Rate:         ~$8.33/hour (vs $10/hour standard)")
        print(f"  Expiry:       Never")
        print(f"  Your Balance: ${student.account_balance:.2f}")
        print(f"  Your Hours:   {package_hours:.1f}")
        print("-" * 50)

        confirm = input(">> Purchase Package Deal? (y/n): ").strip()
        if confirm.lower() != "y":
            print("\n[*] Purchase cancelled.")
            return

        success, message = self.payment_service.purchase_package_deal(student)
        if success:
            print(f"\n[+] {message}")
        else:
            print(f"\n[!] {message}")

    # ── My Profile ──────────────────────────────────────────
    def _my_profile(self, student: Student):
        package_hours = self.ds.get_package_hours(student.user_id)
        active_count = len(self.ds.get_active_future_bookings(student.user_id))

        print("\n" + "-" * 50)
        print("   My Profile")
        print("-" * 50)
        print(f"  Name:           {student.first_name} {student.last_name}")
        print(f"  Student ID:     {student.student_id}")
        print(f"  Email:          {student.email}")
        print(f"  Mobile:         {student.mobile_number}")
        print(f"  Balance:        ${student.account_balance:.2f}")
        print(f"  Package Hours:  {package_hours:.1f}")
        print(f"  Active Bookings: {active_count}/3")
        print(f"  Late Cancellations: {student.late_cancellation_count}")
        print(f"  No-Shows:       {student.no_show_count}")
        total_strikes = student.late_cancellation_count + student.no_show_count
        print(f"  Strikes:        {total_strikes}/3")
        if student.is_banned:
            print(f"  [!] BANNED until {student.ban_end_date}")
        print("-" * 50)

    # ── Transaction History ─────────────────────────────────
    def _transaction_history(self, student: Student):
        transactions = self.payment_service.get_transaction_history(student.user_id)

        print("\n" + "-" * 70)
        print("   Transaction History")
        print("-" * 70)
        if not transactions:
            print("  No transactions found.")
            return

        print(f"  {'Date':<20} {'Type':<20} {'Amount':<12} {'Description'}")
        print("  " + "-" * 70)
        for t in sorted(transactions, key=lambda x: x.transaction_date, reverse=True):
            sign = "+" if t.transaction_type in ("TopUp", "DepositRefund", "BookingRefund") else "-"
            print(f"  {t.transaction_date:<20} {t.transaction_type:<20} "
                  f"{sign}${t.amount:<10.2f} {t.description}")

    # ── Borrow Equipment ────────────────────────────────────
    def _borrow_equipment(self, student: Student):
        active_now = self.ds.get_active_now_bookings(student.user_id)
        if not active_now:
            print("\n[!] Equipment can only be borrowed during your active booked session.")
            return

        print("\n" + "-" * 50)
        print("   Borrow Equipment")
        print("-" * 50)

        for booking in active_now:
            room = self.ds.rooms.get(booking.room_id)
            if not room:
                continue
            print(f"\n  Active Session: {room.room_name} ({booking.start_time}-{booking.end_time})")
            available_eq = self.equipment_service.get_available_equipment(room.room_id)
            if not available_eq:
                print("  No equipment available for this room.")
                continue

            print(f"  {'#':<4} {'Type':<15} {'Status'}")
            print("  " + "-" * 30)
            for i, eq in enumerate(available_eq, 1):
                print(f"  [{i}]  {eq.equipment_type:<15} Available")

            print(f"\n  Deposit required: $100.00 per item")
            print(f"  Your balance: ${student.account_balance:.2f}")

            sel = input("\n>> Select equipment to borrow (#, or B to go back): ").strip()
            if sel.upper() == "B":
                return
            try:
                idx = int(sel)
                if idx < 1 or idx > len(available_eq):
                    print("\n[!] Invalid selection.")
                    return
            except ValueError:
                print("\n[!] Invalid input.")
                return

            selected_eq = available_eq[idx - 1]
            confirm = input(f">> Borrow {selected_eq.equipment_type}? $100 deposit. (y/n): ").strip()
            if confirm.lower() != "y":
                print("\n[*] Borrowing cancelled.")
                return

            success, result = self.equipment_service.borrow_equipment(
                student, booking.booking_id, selected_eq.equipment_id
            )
            if success:
                loan = result
                print(f"\n[+] {selected_eq.equipment_type} borrowed successfully!")
                print(f"    Loan Reference: {loan.loan_id}")
                print(f"    Deposit: $100.00")
                print(f"    Remaining balance: ${student.account_balance:.2f}")
                print(f"    Please return the equipment at the end of your session.")
            else:
                print(f"\n[!] {result}")
            return

        print("\n[!] No active sessions found.")

    # ── Return Equipment ────────────────────────────────────
    def _return_equipment(self, student: Student):
        active_loans = self.equipment_service.get_active_loans_for_student(student.user_id)
        if not active_loans:
            print("\n[!] You have no equipment to return.")
            return

        print("\n" + "-" * 50)
        print("   Return Equipment")
        print("-" * 50)

        print(f"  {'#':<4} {'Loan ID':<12} {'Equipment':<15} {'Booking':<18} {'Deposit'}")
        print("  " + "-" * 55)
        for i, loan in enumerate(active_loans, 1):
            eq = self.ds.equipment.get(loan.equipment_id)
            eq_type = eq.equipment_type if eq else "Unknown"
            booking = self.ds.bookings.get(loan.booking_id)
            bref = booking.booking_reference if booking else "Unknown"
            print(f"  [{i}]  {loan.loan_id:<12} {eq_type:<15} {bref:<18} ${loan.deposit_amount:.2f}")

        try:
            sel = int(input("\n>> Select loan to return (#): ").strip())
            if sel < 1 or sel > len(active_loans):
                print("\n[!] Invalid selection.")
                return
        except ValueError:
            print("\n[!] Invalid input.")
            return

        loan = active_loans[sel - 1]
        eq = self.ds.equipment.get(loan.equipment_id)
        eq_name = eq.equipment_type if eq else "equipment"

        damaged_input = input(f">> Is the {eq_name} damaged? (y/n): ").strip()
        damaged = damaged_input.lower() == "y"

        success, message = self.equipment_service.return_equipment(student, loan.loan_id, damaged)
        if success:
            print(f"\n[+] {message}")
        else:
            print(f"\n[!] {message}")

    # ── Room Details ────────────────────────────────────────
    def _show_room_details(self, room_id):
        """Display detailed room information including equipment."""
        details = self.room_service.get_room_details(room_id)
        if not details:
            print("\n[!] Room not found.")
            return

        room = details["room"]
        print("\n" + "-" * 50)
        print(f"   Room Details: {room.room_name}")
        print("-" * 50)
        print(f"  Building:    {details['building_name']}")
        print(f"  Capacity:    {room.capacity} people")
        print(f"  Price:       ${room.price_per_hour:.2f}/hour")
        print(f"  Status:      {'Available' if room.is_available else 'Unavailable'}")
        print(f"  Equipment:   Table and Chair (included)")

        if details["available_equipment"]:
            print(f"\n  Optional Equipment Available:")
            for eq in details["available_equipment"]:
                print(f"    - {eq.equipment_type} ($100 deposit)")

        if details["damaged_equipment"]:
            print(f"\n  Currently Unavailable:")
            for eq in details["damaged_equipment"]:
                print(f"    - {eq.equipment_type} (under repair)")

        if not details["all_equipment"]:
            print(f"\n  No optional equipment in this room.")

        print("-" * 50)
