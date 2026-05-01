from datetime import datetime, timedelta

from models.user import Student, Admin
from models.building import Building
from models.room import Room
from models.equipment import Equipment
from models.booking import Booking
from models.equipment_loan import EquipmentLoan
from models.package_deal import PackageDeal
from models.transaction import Transaction


def init_mock_data(ds):
    """Initialize realistic mock data for the MSSRB system."""
    # ── Admin ───────────────────────────────────────────
    admin = Admin(
        user_id="admin001", email="admin@monash.edu",
        password="Monash1234!", first_name="System", last_name="Admin",
    )
    ds.users[admin.user_id] = admin

    # ── Students (8 students with varied states) ────────
    alice = Student(
        user_id="stu001", email="alice@student.monash.edu",
        password="Monash1!a", first_name="Alice", last_name="Chen",
        student_id="36668001", mobile_number="0412345678",
        account_balance=320.00,
    )
    bob = Student(
        user_id="stu002", email="bob@student.monash.edu",
        password="Monash1!b", first_name="Bob", last_name="Wang",
        student_id="36668002", mobile_number="0498765432",
        account_balance=45.50,
    )
    charlie = Student(
        user_id="stu003", email="charlie@student.monash.edu",
        password="Monash1!c", first_name="Charlie", last_name="Zhang",
        student_id="36668003", mobile_number="0423456789",
        account_balance=180.00,
    )
    diana = Student(
        user_id="stu004", email="diana@student.monash.edu",
        password="Monash1!d", first_name="Diana", last_name="Li",
        student_id="36668004", mobile_number="0434567890",
        account_balance=500.00,
    )
    ethan = Student(
        user_id="stu005", email="ethan@student.monash.edu",
        password="Monash1!e", first_name="Ethan", last_name="Park",
        student_id="36668005", mobile_number="0445678901",
        account_balance=75.00,
        late_cancellation_count=1, no_show_count=1,
    )
    fiona = Student(
        user_id="stu006", email="fiona@student.monash.edu",
        password="Monash1!f", first_name="Fiona", last_name="Kim",
        student_id="36668006", mobile_number="0456789012",
        account_balance=200.00,
        is_banned=True,
        ban_end_date=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        late_cancellation_count=2, no_show_count=1,
    )
    george = Student(
        user_id="stu007", email="george@student.monash.edu",
        password="Monash1!g", first_name="George", last_name="Tanaka",
        student_id="36668007", mobile_number="0467890123",
        account_balance=850.00,
    )
    hannah = Student(
        user_id="stu008", email="hannah@student.monash.edu",
        password="Monash1!h", first_name="Hannah", last_name="Nguyen",
        student_id="36668008", mobile_number="0478901234",
        account_balance=12.00,
    )

    for s in [alice, bob, charlie, diana, ethan, fiona, george, hannah]:
        ds.users[s.user_id] = s

    # ── Buildings (3 Monash campus buildings) ───────────
    ltb = Building(building_id="bld001", building_name="LTB")
    mth = Building(building_id="bld002", building_name="MTH")
    wds = Building(building_id="bld003", building_name="WDS")
    ds.buildings[ltb.building_id] = ltb
    ds.buildings[mth.building_id] = mth
    ds.buildings[wds.building_id] = wds

    # ── Rooms (10 rooms across 3 buildings) ─────────────
    rooms_data = [
        ("rm001", "LTB-214", "bld001", 2, 10.0),
        ("rm002", "LTB-305", "bld001", 2, 10.0),
        ("rm003", "LTB-110", "bld001", 2, 10.0),
        ("rm004", "MTH-S201", "bld002", 2, 10.0),
        ("rm005", "MTH-S203", "bld002", 2, 10.0),
        ("rm006", "MTH-105", "bld002", 2, 10.0),
        ("rm007", "MTH-301", "bld002", 2, 10.0),
        ("rm008", "WDS-305", "bld003", 2, 10.0),
        ("rm009", "WDS-201", "bld003", 2, 10.0),
        ("rm010", "WDS-102", "bld003", 2, 10.0),
    ]
    for rid, rname, bid, cap, price in rooms_data:
        room = Room(room_id=rid, room_name=rname, building_id=bid,
                    capacity=cap, price_per_hour=price)
        ds.rooms[room.room_id] = room

    # ── Equipment (distributed across rooms) ────────────
    equip_data = [
        ("eq001", "rm001", "Projector"),
        ("eq002", "rm001", "Whiteboard"),
        ("eq003", "rm001", "Monitor"),
        ("eq004", "rm002", "Projector"),
        ("eq005", "rm002", "Monitor"),
        ("eq006", "rm004", "Projector"),
        ("eq007", "rm004", "Whiteboard"),
        ("eq008", "rm005", "Monitor"),
        ("eq009", "rm005", "Whiteboard"),
        ("eq010", "rm006", "Projector"),
        ("eq011", "rm008", "Whiteboard"),
        ("eq012", "rm008", "Monitor"),
        ("eq013", "rm009", "Projector"),
        ("eq014", "rm010", "Monitor"),
    ]
    for eid, rid, etype in equip_data:
        eq = Equipment(equipment_id=eid, room_id=rid, equipment_type=etype)
        ds.equipment[eq.equipment_id] = eq

    # ── Bookings (varied statuses for realism) ──────────
    today = datetime.now()
    past1 = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    past2 = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    past3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    past4 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    future1 = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    future2 = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    future3 = (today + timedelta(days=5)).strftime("%Y-%m-%d")

    bookings_data = [
        ("bk001", "BR-260420-A1B2", "stu001", "rm001", past1,
         "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "AccountBalance",
         "2026-04-20 09:00:00"),
        ("bk002", "BR-260425-C3D4", "stu001", "rm004", future1,
         "14:00", "16:00", 2.0, 20.0, 20.0, "Active", "AccountBalance",
         "2026-04-25 11:00:00"),
        ("bk003", "BR-260418-E5F6", "stu002", "rm002", past2,
         "09:00", "11:00", 2.0, 16.0, 20.0, "Completed", "AccountBalance",
         "2026-04-18 08:30:00"),
        ("bk004", "BR-260422-G7H8", "stu002", "rm005", past3,
         "13:00", "15:00", 2.0, 20.0, 20.0, "Cancelled", "AccountBalance",
         "2026-04-22 10:00:00"),
        ("bk005", "BR-260419-I9J0", "stu003", "rm001", past1,
         "14:00", "17:00", 3.0, 30.0, 30.0, "Completed", "PackageHours",
         "2026-04-19 13:00:00"),
        ("bk006", "BR-260421-K1L2", "stu003", "rm006", past4,
         "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "PackageHours",
         "2026-04-21 09:30:00"),
        ("bk007", "BR-260426-M3N4", "stu003", "rm004", future2,
         "09:00", "12:00", 3.0, 30.0, 30.0, "Active", "PackageHours",
         "2026-04-26 08:00:00"),
        ("bk008", "BR-260420-O5P6", "stu005", "rm008", past1,
         "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "AccountBalance",
         "2026-04-20 09:30:00"),
        ("bk009", "BR-260423-Q7R8", "stu005", "rm009", past3,
         "15:00", "17:00", 2.0, 20.0, 20.0, "Cancelled", "AccountBalance",
         "2026-04-23 14:50:00"),
        ("bk010", "BR-260424-S9T0", "stu005", "rm010", past4,
         "11:00", "13:00", 2.0, 20.0, 20.0, "NoShow", "AccountBalance",
         "2026-04-24 10:00:00"),
        ("bk011", "BR-260422-U1V2", "stu007", "rm007", past2,
         "10:00", "13:00", 3.0, 30.0, 30.0, "Completed", "AccountBalance",
         "2026-04-22 09:00:00"),
        ("bk012", "BR-260427-W3X4", "stu007", "rm001", future1,
         "09:00", "11:00", 2.0, 20.0, 20.0, "Active", "AccountBalance",
         "2026-04-27 08:00:00"),
        ("bk013", "BR-260427-Y5Z6", "stu007", "rm008", future3,
         "14:00", "16:00", 2.0, 20.0, 20.0, "Active", "AccountBalance",
         "2026-04-27 08:30:00"),
    ]

    for bid, bref, sid, rid, date, st, et, dur, cost, ocost, status, pay, created in bookings_data:
        b = Booking(
            booking_id=bid, booking_reference=bref, student_id=sid,
            room_id=rid, date=date, start_time=st, end_time=et,
            duration=dur, total_cost=cost, original_cost=ocost,
            status=status, payment_method=pay, created_at=created,
        )
        ds.bookings[b.booking_id] = b

    # ── Package Deals ───────────────────────────────────
    pd1 = PackageDeal(
        package_id="pd001", student_id="stu003",
        price=100.0, total_hours=12.0, remaining_hours=7.0,
        purchase_date="2026-04-10 10:00:00",
    )
    pd2 = PackageDeal(
        package_id="pd002", student_id="stu003",
        price=100.0, total_hours=12.0, remaining_hours=12.0,
        purchase_date="2026-04-20 15:00:00",
    )
    pd3 = PackageDeal(
        package_id="pd003", student_id="stu007",
        price=100.0, total_hours=12.0, remaining_hours=12.0,
        purchase_date="2026-04-18 09:00:00",
    )
    ds.package_deals[pd1.package_id] = pd1
    ds.package_deals[pd2.package_id] = pd2
    ds.package_deals[pd3.package_id] = pd3

    # ── Equipment Loans (varied states) ─────────────────
    el1 = EquipmentLoan(
        loan_id="el001", student_id="stu001", booking_id="bk001",
        equipment_id="eq001", deposit_amount=100.0,
        is_returned=True, is_damaged=False,
        loan_date="2026-04-20 10:15:00",
    )
    el2 = EquipmentLoan(
        loan_id="el002", student_id="stu003", booking_id="bk005",
        equipment_id="eq002", deposit_amount=100.0,
        is_returned=True, is_damaged=False,
        loan_date="2026-04-19 14:10:00",
    )
    el3 = EquipmentLoan(
        loan_id="el003", student_id="stu007", booking_id="bk011",
        equipment_id="eq005", deposit_amount=100.0,
        is_returned=True, is_damaged=True,
        loan_date="2026-04-22 10:20:00",
    )
    ds.equipment_loans[el1.loan_id] = el1
    ds.equipment_loans[el2.loan_id] = el2
    ds.equipment_loans[el3.loan_id] = el3

    eq005 = ds.equipment.get("eq005")
    if eq005:
        eq005.is_damaged = True
        eq005.is_available = False

    # ── Transactions ────────────────────────────────────
    tx_data = [
        ("tx001", "stu001", 200.00, "TopUp", "2026-04-15 09:00:00",
         "Account top-up of $200.00"),
        ("tx002", "stu001", 200.00, "TopUp", "2026-04-18 14:00:00",
         "Account top-up of $200.00"),
        ("tx003", "stu001", 20.00, "BookingPayment", "2026-04-20 09:00:00",
         "Booking BR-260420-A1B2 - LTB-214"),
        ("tx004", "stu001", 100.00, "DepositCharge", "2026-04-20 10:15:00",
         "Equipment deposit for Projector (eq001)"),
        ("tx005", "stu001", 100.00, "DepositRefund", "2026-04-20 12:05:00",
         "Equipment deposit refund for Projector"),
        ("tx006", "stu001", 20.00, "BookingPayment", "2026-04-25 11:00:00",
         "Booking BR-260425-C3D4 - MTH-S201"),
        ("tx007", "stu002", 50.00, "TopUp", "2026-04-17 11:00:00",
         "Account top-up of $50.00"),
        ("tx008", "stu002", 16.00, "BookingPayment", "2026-04-18 08:30:00",
         "Booking BR-260418-E5F6 - LTB-305"),
        ("tx009", "stu002", 4.00, "PromoDiscount", "2026-04-18 08:30:00",
         "NEWBIE20 discount on BR-260418-E5F6"),
        ("tx010", "stu002", 20.00, "BookingRefund", "2026-04-22 12:00:00",
         "Refund for cancelled booking BR-260422-G7H8"),
        ("tx011", "stu003", 300.00, "TopUp", "2026-04-08 10:00:00",
         "Account top-up of $300.00"),
        ("tx012", "stu003", 100.00, "PackagePurchase", "2026-04-10 10:00:00",
         "Package Deal purchase: $100 for 12 hours"),
        ("tx013", "stu003", 100.00, "PackagePurchase", "2026-04-20 15:00:00",
         "Package Deal purchase: $100 for 12 hours"),
        ("tx014", "stu003", 0.00, "BookingPayment", "2026-04-19 13:00:00",
         "Booking BR-260419-I9J0 - LTB-214 (Package Hours)"),
        ("tx015", "stu003", 100.00, "DepositCharge", "2026-04-19 14:10:00",
         "Equipment deposit for Whiteboard (eq002)"),
        ("tx016", "stu003", 100.00, "DepositRefund", "2026-04-19 17:05:00",
         "Equipment deposit refund for Whiteboard"),
        ("tx017", "stu005", 100.00, "TopUp", "2026-04-19 08:00:00",
         "Account top-up of $100.00"),
        ("tx018", "stu005", 20.00, "BookingPayment", "2026-04-20 09:30:00",
         "Booking BR-260420-O5P6 - WDS-305"),
        ("tx019", "stu005", 20.00, "BookingRefund", "2026-04-23 14:55:00",
         "Refund for cancelled booking BR-260423-Q7R8"),
        ("tx020", "stu006", 300.00, "TopUp", "2026-04-05 10:00:00",
         "Account top-up of $300.00"),
        ("tx021", "stu007", 500.00, "TopUp", "2026-04-15 09:00:00",
         "Account top-up of $500.00"),
        ("tx022", "stu007", 500.00, "TopUp", "2026-04-17 14:00:00",
         "Account top-up of $500.00"),
        ("tx023", "stu007", 100.00, "PackagePurchase", "2026-04-18 09:00:00",
         "Package Deal purchase: $100 for 12 hours"),
        ("tx024", "stu007", 30.00, "BookingPayment", "2026-04-22 09:00:00",
         "Booking BR-260422-U1V2 - MTH-301"),
        ("tx025", "stu007", 100.00, "DepositCharge", "2026-04-22 10:20:00",
         "Equipment deposit for Monitor (eq005)"),
        ("tx026", "stu007", 0.00, "DepositCharge", "2026-04-22 13:10:00",
         "Deposit forfeited - Monitor returned damaged"),
        ("tx027", "stu008", 20.00, "TopUp", "2026-04-25 16:00:00",
         "Account top-up of $20.00"),
    ]

    for tid, sid, amt, ttype, tdate, desc in tx_data:
        tx = Transaction(
            transaction_id=tid, student_id=sid,
            amount=amt, transaction_type=ttype,
            transaction_date=tdate, description=desc,
        )
        ds.transactions[tx.transaction_id] = tx

    # ── Promo Codes Used ────────────────────────────────
    ds.promo_codes_used.add("stu002")

    ds.save_all()


# ── Query Helper Methods (mixin-style) ──────────────────
# These are added as methods to DataService via _attach_helpers

def _get_student_by_email(self, email):
    for u in self.users.values():
        if isinstance(u, Student) and u.email == email:
            return u
    return None


def _get_user_by_email(self, email):
    for u in self.users.values():
        if u.email == email:
            return u
    return None


def _get_building_by_name(self, name):
    for b in self.buildings.values():
        if b.building_name == name:
            return b
    return None


def _get_rooms_by_building(self, building_id):
    return [r for r in self.rooms.values() if r.building_id == building_id]


def _get_equipment_by_room(self, room_id):
    return [e for e in self.equipment.values() if e.room_id == room_id]


def _get_bookings_for_student(self, student_id):
    return [b for b in self.bookings.values() if b.student_id == student_id]


def _get_active_future_bookings(self, student_id):
    return [b for b in self.bookings.values()
            if b.student_id == student_id and b.is_future()]


def _get_active_now_bookings(self, student_id):
    return [b for b in self.bookings.values()
            if b.student_id == student_id and b.is_active_now()]


def _get_package_hours(self, student_id):
    total = 0.0
    for pd in self.package_deals.values():
        if pd.student_id == student_id:
            total += pd.remaining_hours
    return total


def _deduct_package_hours(self, student_id, hours):
    remaining = hours
    for pd in self.package_deals.values():
        if pd.student_id == student_id and pd.remaining_hours > 0:
            if pd.remaining_hours >= remaining:
                pd.remaining_hours -= remaining
                remaining = 0
                break
            else:
                remaining -= pd.remaining_hours
                pd.remaining_hours = 0
    return remaining == 0


def _restore_package_hours(self, student_id, hours):
    for pd in self.package_deals.values():
        if pd.student_id == student_id:
            pd.remaining_hours += hours
            return
    new_pd = PackageDeal(student_id=student_id, remaining_hours=hours,
                         total_hours=0, price=0)
    self.package_deals[new_pd.package_id] = new_pd


def _has_room_future_bookings(self, room_id):
    for b in self.bookings.values():
        if b.room_id == room_id and b.is_future():
            return True
    return False


def _check_room_conflict(self, room_id, date, start_time, end_time):
    for b in self.bookings.values():
        if (b.room_id == room_id and b.date == date
                and b.status == Booking.STATUS_ACTIVE):
            if not (end_time <= b.start_time or start_time >= b.end_time):
                return True
    return False


def _room_exists_in_building(self, room_name, building_id):
    for r in self.rooms.values():
        if r.room_name == room_name and r.building_id == building_id:
            return True
    return False


def _get_equipment_loans_for_booking(self, booking_id):
    return [el for el in self.equipment_loans.values()
            if el.booking_id == booking_id and not el.is_returned]


def attach_helpers(ds):
    """Attach query helper methods to a DataService instance."""
    import types
    ds.get_student_by_email = types.MethodType(_get_student_by_email, ds)
    ds.get_user_by_email = types.MethodType(_get_user_by_email, ds)
    ds.get_building_by_name = types.MethodType(_get_building_by_name, ds)
    ds.get_rooms_by_building = types.MethodType(_get_rooms_by_building, ds)
    ds.get_equipment_by_room = types.MethodType(_get_equipment_by_room, ds)
    ds.get_bookings_for_student = types.MethodType(_get_bookings_for_student, ds)
    ds.get_active_future_bookings = types.MethodType(_get_active_future_bookings, ds)
    ds.get_active_now_bookings = types.MethodType(_get_active_now_bookings, ds)
    ds.get_package_hours = types.MethodType(_get_package_hours, ds)
    ds.deduct_package_hours = types.MethodType(_deduct_package_hours, ds)
    ds.restore_package_hours = types.MethodType(_restore_package_hours, ds)
    ds.has_room_future_bookings = types.MethodType(_has_room_future_bookings, ds)
    ds.check_room_conflict = types.MethodType(_check_room_conflict, ds)
    ds.room_exists_in_building = types.MethodType(_room_exists_in_building, ds)
    ds.get_equipment_loans_for_booking = types.MethodType(_get_equipment_loans_for_booking, ds)
