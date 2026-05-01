import csv
import os

from models.user import Student, Admin
from models.building import Building
from models.room import Room
from models.equipment import Equipment
from models.booking import Booking
from models.equipment_loan import EquipmentLoan
from models.package_deal import PackageDeal
from models.transaction import Transaction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class DataService:
    def __init__(self):
        self.users = {}        # user_id -> User
        self.buildings = {}    # building_id -> Building
        self.rooms = {}        # room_id -> Room
        self.equipment = {}    # equipment_id -> Equipment
        self.bookings = {}     # booking_id -> Booking
        self.equipment_loans = {}  # loan_id -> EquipmentLoan
        self.package_deals = {}    # package_id -> PackageDeal
        self.transactions = {}     # transaction_id -> Transaction
        self.promo_codes_used = set()  # set of student_ids that used promo

        os.makedirs(DATA_DIR, exist_ok=True)
        self._load_all()

    # ── File Paths ──────────────────────────────────────────
    def _path(self, filename):
        return os.path.join(DATA_DIR, filename)

    # ── CSV Helpers ─────────────────────────────────────────
    def _read_csv(self, filename):
        filepath = self._path(filename)
        if not os.path.exists(filepath):
            return []
        rows = []
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    def _write_csv(self, filename, fieldnames, records):
        filepath = self._path(filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)

    # ── Load All Data ───────────────────────────────────────
    def _load_all(self):
        self._load_users()
        self._load_buildings()
        self._load_rooms()
        self._load_equipment()
        self._load_bookings()
        self._load_equipment_loans()
        self._load_package_deals()
        self._load_transactions()
        self._load_promo_codes()

        if not self.users:
            self._init_mock_data()

    def _load_users(self):
        for row in self._read_csv("users.csv"):
            if row.get("role") == "student":
                user = Student(
                    user_id=row["user_id"], email=row["email"],
                    password=row["password"], first_name=row["first_name"],
                    last_name=row["last_name"],
                    student_id=row.get("student_id", ""),
                    mobile_number=row.get("mobile_number", ""),
                    account_balance=row.get("account_balance", 0),
                    is_banned=row.get("is_banned", "False") == "True",
                    ban_end_date=row.get("ban_end_date", ""),
                    late_cancellation_count=row.get("late_cancellation_count", 0),
                    no_show_count=row.get("no_show_count", 0),
                )
                self.users[user.user_id] = user
            elif row.get("role") == "admin":
                user = Admin(
                    user_id=row["user_id"], email=row["email"],
                    password=row["password"], first_name=row["first_name"],
                    last_name=row["last_name"],
                )
                self.users[user.user_id] = user

    def _load_buildings(self):
        for row in self._read_csv("buildings.csv"):
            b = Building(building_id=row["building_id"],
                         building_name=row["building_name"])
            self.buildings[b.building_id] = b

    def _load_rooms(self):
        for row in self._read_csv("rooms.csv"):
            r = Room(
                room_id=row["room_id"], room_name=row["room_name"],
                building_id=row["building_id"],
                capacity=row.get("capacity", 2),
                price_per_hour=row.get("price_per_hour", 10.0),
                is_available=row.get("is_available", "True") == "True",
            )
            self.rooms[r.room_id] = r

    def _load_equipment(self):
        for row in self._read_csv("equipment.csv"):
            e = Equipment(
                equipment_id=row["equipment_id"],
                room_id=row["room_id"],
                equipment_type=row["equipment_type"],
                is_available=row.get("is_available", "True") == "True",
                is_damaged=row.get("is_damaged", "False") == "True",
            )
            self.equipment[e.equipment_id] = e

    def _load_bookings(self):
        for row in self._read_csv("bookings.csv"):
            b = Booking(
                booking_id=row["booking_id"],
                booking_reference=row["booking_reference"],
                student_id=row["student_id"],
                room_id=row["room_id"],
                date=row["date"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                duration=row.get("duration", 0),
                total_cost=row.get("total_cost", 0),
                original_cost=row.get("original_cost", row.get("total_cost", 0)),
                status=row.get("status", ""),
                payment_method=row.get("payment_method", ""),
                created_at=row.get("created_at", ""),
            )
            self.bookings[b.booking_id] = b

    def _load_equipment_loans(self):
        for row in self._read_csv("equipment_loans.csv"):
            el = EquipmentLoan(
                loan_id=row["loan_id"],
                student_id=row["student_id"],
                booking_id=row["booking_id"],
                equipment_id=row["equipment_id"],
                deposit_amount=row.get("deposit_amount", 100),
                is_returned=row.get("is_returned", "False") == "True",
                is_damaged=row.get("is_damaged", "False") == "True",
                loan_date=row.get("loan_date", ""),
            )
            self.equipment_loans[el.loan_id] = el

    def _load_package_deals(self):
        for row in self._read_csv("package_deals.csv"):
            pd = PackageDeal(
                package_id=row["package_id"],
                student_id=row["student_id"],
                price=row.get("price", 100),
                total_hours=row.get("total_hours", 12),
                remaining_hours=row.get("remaining_hours", 12),
                purchase_date=row.get("purchase_date", ""),
            )
            self.package_deals[pd.package_id] = pd

    def _load_transactions(self):
        for row in self._read_csv("transactions.csv"):
            t = Transaction(
                transaction_id=row["transaction_id"],
                student_id=row["student_id"],
                amount=row.get("amount", 0),
                transaction_type=row.get("transaction_type", ""),
                transaction_date=row.get("transaction_date", ""),
                description=row.get("description", ""),
            )
            self.transactions[t.transaction_id] = t

    def _load_promo_codes(self):
        filepath = self._path("promo_codes.csv")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and line != "student_id":
                        self.promo_codes_used.add(line)

    # ── Save All Data ───────────────────────────────────────
    def save_all(self):
        self._save_users()
        self._save_buildings()
        self._save_rooms()
        self._save_equipment()
        self._save_bookings()
        self._save_equipment_loans()
        self._save_package_deals()
        self._save_transactions()
        self._save_promo_codes()

    def _save_users(self):
        fieldnames = ["user_id", "email", "password", "first_name", "last_name",
                       "role", "student_id", "mobile_number", "account_balance",
                       "is_banned", "ban_end_date", "late_cancellation_count", "no_show_count"]
        records = []
        for u in self.users.values():
            records.append(u.to_dict())
        self._write_csv("users.csv", fieldnames, records)

    def _save_buildings(self):
        fieldnames = ["building_id", "building_name"]
        records = [b.to_dict() for b in self.buildings.values()]
        self._write_csv("buildings.csv", fieldnames, records)

    def _save_rooms(self):
        fieldnames = ["room_id", "room_name", "building_id", "capacity",
                       "price_per_hour", "is_available"]
        records = [r.to_dict() for r in self.rooms.values()]
        self._write_csv("rooms.csv", fieldnames, records)

    def _save_equipment(self):
        fieldnames = ["equipment_id", "room_id", "equipment_type",
                       "is_available", "is_damaged"]
        records = [e.to_dict() for e in self.equipment.values()]
        self._write_csv("equipment.csv", fieldnames, records)

    def _save_bookings(self):
        fieldnames = ["booking_id", "booking_reference", "student_id", "room_id",
                       "date", "start_time", "end_time", "duration", "total_cost",
                       "original_cost", "status", "payment_method", "created_at"]
        records = [b.to_dict() for b in self.bookings.values()]
        self._write_csv("bookings.csv", fieldnames, records)

    def _save_equipment_loans(self):
        fieldnames = ["loan_id", "student_id", "booking_id", "equipment_id",
                       "deposit_amount", "is_returned", "is_damaged", "loan_date"]
        records = [el.to_dict() for el in self.equipment_loans.values()]
        self._write_csv("equipment_loans.csv", fieldnames, records)

    def _save_package_deals(self):
        fieldnames = ["package_id", "student_id", "price", "total_hours",
                       "remaining_hours", "purchase_date"]
        records = [pd.to_dict() for pd in self.package_deals.values()]
        self._write_csv("package_deals.csv", fieldnames, records)

    def _save_transactions(self):
        fieldnames = ["transaction_id", "student_id", "amount", "transaction_type",
                       "transaction_date", "description"]
        records = [t.to_dict() for t in self.transactions.values()]
        self._write_csv("transactions.csv", fieldnames, records)

    def _save_promo_codes(self):
        filepath = self._path("promo_codes.csv")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("student_id\n")
            for sid in self.promo_codes_used:
                f.write(f"{sid}\n")

    # ── Mock Data Initialization ────────────────────────────
    def _init_mock_data(self):
        from datetime import datetime, timedelta

        # ── Admin ───────────────────────────────────────────
        admin = Admin(
            user_id="admin001", email="admin@monash.edu",
            password="Monash1234!", first_name="System", last_name="Admin",
        )
        self.users[admin.user_id] = admin

        # ── Students (8 students with varied states) ────────
        # Alice: active user, has balance, has package deal, has bookings
        alice = Student(
            user_id="stu001", email="alice@student.monash.edu",
            password="Monash1!a", first_name="Alice", last_name="Chen",
            student_id="36668001", mobile_number="0412345678",
            account_balance=320.00,
        )
        # Bob: low balance, has used promo code, has 1 past booking
        bob = Student(
            user_id="stu002", email="bob@student.monash.edu",
            password="Monash1!b", first_name="Bob", last_name="Wang",
            student_id="36668002", mobile_number="0498765432",
            account_balance=45.50,
        )
        # Charlie: heavy user, has package deal, multiple bookings
        charlie = Student(
            user_id="stu003", email="charlie@student.monash.edu",
            password="Monash1!c", first_name="Charlie", last_name="Zhang",
            student_id="36668003", mobile_number="0423456789",
            account_balance=180.00,
        )
        # Diana: new user, just registered, no bookings yet
        diana = Student(
            user_id="stu004", email="diana@student.monash.edu",
            password="Monash1!d", first_name="Diana", last_name="Li",
            student_id="36668004", mobile_number="0434567890",
            account_balance=500.00,
        )
        # Ethan: has 2 strikes (1 late cancel + 1 no-show), close to ban
        ethan = Student(
            user_id="stu005", email="ethan@student.monash.edu",
            password="Monash1!e", first_name="Ethan", last_name="Park",
            student_id="36668005", mobile_number="0445678901",
            account_balance=75.00,
            late_cancellation_count=1, no_show_count=1,
        )
        # Fiona: currently banned (3 strikes)
        fiona = Student(
            user_id="stu006", email="fiona@student.monash.edu",
            password="Monash1!f", first_name="Fiona", last_name="Kim",
            student_id="36668006", mobile_number="0456789012",
            account_balance=200.00,
            is_banned=True,
            ban_end_date=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            late_cancellation_count=2, no_show_count=1,
        )
        # George: high balance, package deal user
        george = Student(
            user_id="stu007", email="george@student.monash.edu",
            password="Monash1!g", first_name="George", last_name="Tanaka",
            student_id="36668007", mobile_number="0467890123",
            account_balance=850.00,
        )
        # Hannah: minimal balance
        hannah = Student(
            user_id="stu008", email="hannah@student.monash.edu",
            password="Monash1!h", first_name="Hannah", last_name="Nguyen",
            student_id="36668008", mobile_number="0478901234",
            account_balance=12.00,
        )

        for s in [alice, bob, charlie, diana, ethan, fiona, george, hannah]:
            self.users[s.user_id] = s

        # ── Buildings (3 Monash campus buildings) ───────────
        ltb = Building(building_id="bld001", building_name="LTB")
        mth = Building(building_id="bld002", building_name="MTH")
        wds = Building(building_id="bld003", building_name="WDS")
        self.buildings[ltb.building_id] = ltb
        self.buildings[mth.building_id] = mth
        self.buildings[wds.building_id] = wds

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
            self.rooms[room.room_id] = room

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
            self.equipment[eq.equipment_id] = eq

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
            # Alice: 1 completed, 1 active future
            ("bk001", "BR-260420-A1B2", "stu001", "rm001", past1,
             "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "AccountBalance",
             "2026-04-20 09:00:00"),
            ("bk002", "BR-260425-C3D4", "stu001", "rm004", future1,
             "14:00", "16:00", 2.0, 20.0, 20.0, "Active", "AccountBalance",
             "2026-04-25 11:00:00"),
            # Bob: 1 completed (used promo), 1 cancelled
            ("bk003", "BR-260418-E5F6", "stu002", "rm002", past2,
             "09:00", "11:00", 2.0, 16.0, 20.0, "Completed", "AccountBalance",
             "2026-04-18 08:30:00"),
            ("bk004", "BR-260422-G7H8", "stu002", "rm005", past3,
             "13:00", "15:00", 2.0, 20.0, 20.0, "Cancelled", "AccountBalance",
             "2026-04-22 10:00:00"),
            # Charlie: 2 completed, 1 active future, uses package hours
            ("bk005", "BR-260419-I9J0", "stu003", "rm001", past1,
             "14:00", "17:00", 3.0, 30.0, 30.0, "Completed", "PackageHours",
             "2026-04-19 13:00:00"),
            ("bk006", "BR-260421-K1L2", "stu003", "rm006", past4,
             "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "PackageHours",
             "2026-04-21 09:30:00"),
            ("bk007", "BR-260426-M3N4", "stu003", "rm004", future2,
             "09:00", "12:00", 3.0, 30.0, 30.0, "Active", "PackageHours",
             "2026-04-26 08:00:00"),
            # Ethan: 1 completed, 1 late cancellation (strike), 1 no-show (strike)
            ("bk008", "BR-260420-O5P6", "stu005", "rm008", past1,
             "10:00", "12:00", 2.0, 20.0, 20.0, "Completed", "AccountBalance",
             "2026-04-20 09:30:00"),
            ("bk009", "BR-260423-Q7R8", "stu005", "rm009", past3,
             "15:00", "17:00", 2.0, 20.0, 20.0, "Cancelled", "AccountBalance",
             "2026-04-23 14:50:00"),
            ("bk010", "BR-260424-S9T0", "stu005", "rm010", past4,
             "11:00", "13:00", 2.0, 20.0, 20.0, "NoShow", "AccountBalance",
             "2026-04-24 10:00:00"),
            # George: 1 completed, 2 active future
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
            self.bookings[b.booking_id] = b

        # ── Package Deals ───────────────────────────────────
        # Charlie: purchased 2 packages, used some hours
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
        # George: purchased 1 package, not yet used
        pd3 = PackageDeal(
            package_id="pd003", student_id="stu007",
            price=100.0, total_hours=12.0, remaining_hours=12.0,
            purchase_date="2026-04-18 09:00:00",
        )
        self.package_deals[pd1.package_id] = pd1
        self.package_deals[pd2.package_id] = pd2
        self.package_deals[pd3.package_id] = pd3

        # ── Equipment Loans (varied states) ─────────────────
        # Alice borrowed and returned a projector (past booking)
        el1 = EquipmentLoan(
            loan_id="el001", student_id="stu001", booking_id="bk001",
            equipment_id="eq001", deposit_amount=100.0,
            is_returned=True, is_damaged=False,
            loan_date="2026-04-20 10:15:00",
        )
        # Charlie borrowed and returned a whiteboard (past booking)
        el2 = EquipmentLoan(
            loan_id="el002", student_id="stu003", booking_id="bk005",
            equipment_id="eq002", deposit_amount=100.0,
            is_returned=True, is_damaged=False,
            loan_date="2026-04-19 14:10:00",
        )
        # George borrowed a monitor and returned it damaged
        el3 = EquipmentLoan(
            loan_id="el003", student_id="stu007", booking_id="bk011",
            equipment_id="eq005", deposit_amount=100.0,
            is_returned=True, is_damaged=True,
            loan_date="2026-04-22 10:20:00",
        )
        self.equipment_loans[el1.loan_id] = el1
        self.equipment_loans[el2.loan_id] = el2
        self.equipment_loans[el3.loan_id] = el3

        # Mark the damaged equipment
        eq005 = self.equipment.get("eq005")
        if eq005:
            eq005.is_damaged = True
            eq005.is_available = False

        # ── Transactions ────────────────────────────────────
        tx_data = [
            # Alice: 2 top-ups, 1 booking payment, 1 deposit + refund
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
            # Bob: 1 top-up, 1 promo booking, 1 cancelled refund
            ("tx007", "stu002", 50.00, "TopUp", "2026-04-17 11:00:00",
             "Account top-up of $50.00"),
            ("tx008", "stu002", 16.00, "BookingPayment", "2026-04-18 08:30:00",
             "Booking BR-260418-E5F6 - LTB-305"),
            ("tx009", "stu002", 4.00, "PromoDiscount", "2026-04-18 08:30:00",
             "NEWBIE20 discount on BR-260418-E5F6"),
            ("tx010", "stu002", 20.00, "BookingRefund", "2026-04-22 12:00:00",
             "Refund for cancelled booking BR-260422-G7H8"),
            # Charlie: 2 top-ups, 2 package purchases, 2 booking payments
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
            # Diana: no transactions yet (new user)
            # Ethan: 1 top-up, 1 booking, 1 late cancel refund
            ("tx017", "stu005", 100.00, "TopUp", "2026-04-19 08:00:00",
             "Account top-up of $100.00"),
            ("tx018", "stu005", 20.00, "BookingPayment", "2026-04-20 09:30:00",
             "Booking BR-260420-O5P6 - WDS-305"),
            ("tx019", "stu005", 20.00, "BookingRefund", "2026-04-23 14:55:00",
             "Refund for cancelled booking BR-260423-Q7R8"),
            # Fiona: 1 top-up, 1 booking payment
            ("tx020", "stu006", 300.00, "TopUp", "2026-04-05 10:00:00",
             "Account top-up of $300.00"),
            # George: 1 top-up, 1 package, 1 booking, 1 deposit forfeited
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
            # Hannah: 1 small top-up
            ("tx027", "stu008", 20.00, "TopUp", "2026-04-25 16:00:00",
             "Account top-up of $20.00"),
        ]

        for tid, sid, amt, ttype, tdate, desc in tx_data:
            tx = Transaction(
                transaction_id=tid, student_id=sid,
                amount=amt, transaction_type=ttype,
                transaction_date=tdate, description=desc,
            )
            self.transactions[tx.transaction_id] = tx

        # ── Promo Codes Used ────────────────────────────────
        self.promo_codes_used.add("stu002")  # Bob used NEWBIE20

        self.save_all()

    # ── Helper: get student by email ────────────────────────
    def get_student_by_email(self, email):
        for u in self.users.values():
            if isinstance(u, Student) and u.email == email:
                return u
        return None

    def get_user_by_email(self, email):
        for u in self.users.values():
            if u.email == email:
                return u
        return None

    def get_building_by_name(self, name):
        for b in self.buildings.values():
            if b.building_name == name:
                return b
        return None

    def get_rooms_by_building(self, building_id):
        return [r for r in self.rooms.values() if r.building_id == building_id]

    def get_equipment_by_room(self, room_id):
        return [e for e in self.equipment.values() if e.room_id == room_id]

    def get_bookings_for_student(self, student_id):
        return [b for b in self.bookings.values() if b.student_id == student_id]

    def get_active_future_bookings(self, student_id):
        return [b for b in self.bookings.values()
                if b.student_id == student_id and b.is_future()]

    def get_active_now_bookings(self, student_id):
        return [b for b in self.bookings.values()
                if b.student_id == student_id and b.is_active_now()]

    def get_package_hours(self, student_id):
        total = 0.0
        for pd in self.package_deals.values():
            if pd.student_id == student_id:
                total += pd.remaining_hours
        return total

    def deduct_package_hours(self, student_id, hours):
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

    def restore_package_hours(self, student_id, hours):
        for pd in self.package_deals.values():
            if pd.student_id == student_id:
                pd.remaining_hours += hours
                return
        new_pd = PackageDeal(student_id=student_id, remaining_hours=hours,
                             total_hours=0, price=0)
        self.package_deals[new_pd.package_id] = new_pd

    def has_room_future_bookings(self, room_id):
        for b in self.bookings.values():
            if b.room_id == room_id and b.is_future():
                return True
        return False

    def check_room_conflict(self, room_id, date, start_time, end_time):
        for b in self.bookings.values():
            if (b.room_id == room_id and b.date == date
                    and b.status == Booking.STATUS_ACTIVE):
                if not (end_time <= b.start_time or start_time >= b.end_time):
                    return True
        return False

    def room_exists_in_building(self, room_name, building_id):
        for r in self.rooms.values():
            if r.room_name == room_name and r.building_id == building_id:
                return True
        return False

    def get_equipment_loans_for_booking(self, booking_id):
        return [el for el in self.equipment_loans.values()
                if el.booking_id == booking_id and not el.is_returned]
