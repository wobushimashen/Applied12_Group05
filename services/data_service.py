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

        # Attach query helper methods from data_init
        from services.data_init import attach_helpers
        attach_helpers(self)

        self._load_all()

    # 鈹€鈹€ File Paths 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    def _path(self, filename):
        return os.path.join(DATA_DIR, filename)

    # 鈹€鈹€ CSV Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    def _read_csv(self, filename):
        filepath = self._path(filename)
        if not os.path.exists(filepath):
            return []
        rows = []
        try:
            with open(filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        except (OSError, csv.Error) as exc:
            print(f"[!] Could not read {filename}: {exc}")
            return []
        return rows

    def _write_csv(self, filename, fieldnames, records):
        filepath = self._path(filename)
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in records:
                    writer.writerow(record)
        except (OSError, csv.Error) as exc:
            print(f"[!] Could not write {filename}: {exc}")

    # 鈹€鈹€ Load All Data 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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
            from services.data_init import init_mock_data
            init_mock_data(self)

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
                room_type=row.get("room_type", ""),
                capacity_min=row.get("capacity_min"),
                capacity_max=row.get("capacity_max"),
                capacity=row.get("capacity", 2),
                price_per_hour=row.get("price_per_hour", 10.0),
                standard_equipment=row.get("standard_equipment", ""),
                opening_time=row.get("opening_time", "08:00"),
                closing_time=row.get("closing_time", "22:00"),
                minimum_duration=row.get("minimum_duration"),
                advance_notice_hours=row.get("advance_notice_hours"),
                late_cancellation_refund_rate=row.get("late_cancellation_refund_rate"),
                no_show_refund_rate=row.get("no_show_refund_rate"),
                late_cancellation_threshold_minutes=row.get(
                    "late_cancellation_threshold_minutes", 30),
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

    # 鈹€鈹€ Save All Data 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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
        fieldnames = [
            "room_id", "room_name", "building_id", "room_type",
            "capacity_min", "capacity_max", "capacity", "price_per_hour",
            "standard_equipment", "opening_time", "closing_time",
            "minimum_duration", "advance_notice_hours",
            "late_cancellation_refund_rate", "no_show_refund_rate",
            "late_cancellation_threshold_minutes", "is_available",
        ]
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

