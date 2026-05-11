from datetime import datetime, timedelta

from models.booking import Booking
from models.building import Building
from models.equipment import Equipment
from models.package_deal import PackageDeal
from models.room import Room
from models.user import Admin, Student
from services.data_init import attach_helpers


def future_date(days=1):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def past_date(days=1):
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


def active_times():
    start = datetime.now() - timedelta(minutes=15)
    end = datetime.now() + timedelta(minutes=45)
    return start.strftime("%Y-%m-%d"), start.strftime("%H:%M"), end.strftime("%H:%M")


class InMemoryDataService:
    def __init__(self):
        self.users = {}
        self.buildings = {}
        self.rooms = {}
        self.equipment = {}
        self.bookings = {}
        self.equipment_loans = {}
        self.package_deals = {}
        self.transactions = {}
        self.promo_codes_used = set()
        self.save_count = 0
        attach_helpers(self)

    def save_all(self):
        self.save_count += 1


def build_data_service():
    ds = InMemoryDataService()

    admin = Admin(
        user_id="admin001",
        email="admin@monash.edu",
        password="AdminPass1",
        first_name="Admin",
        last_name="User",
    )
    student = Student(
        user_id="stu001",
        email="alice@student.monash.edu",
        password="Password1",
        first_name="Alice",
        last_name="Chen",
        student_id="30000001",
        mobile_number="0400000001",
        account_balance=200.0,
    )
    other_student = Student(
        user_id="stu002",
        email="bob@student.monash.edu",
        password="Password2",
        first_name="Bob",
        last_name="Wang",
        student_id="30000002",
        mobile_number="0400000002",
        account_balance=25.0,
    )
    seeded_student1 = Student(
        user_id="student1",
        email="student1@student.monash.edu",
        password="Student123!",
        first_name="Student",
        last_name="One",
        student_id="36668101",
        mobile_number="0411111111",
        account_balance=150.0,
    )
    seeded_student2 = Student(
        user_id="student2",
        email="student2@student.monash.edu",
        password="Student123!",
        first_name="Student",
        last_name="Two",
        student_id="36668102",
        mobile_number="0422222222",
        account_balance=120.0,
    )
    ds.users[admin.user_id] = admin
    ds.users[student.user_id] = student
    ds.users[other_student.user_id] = other_student
    ds.users[seeded_student1.user_id] = seeded_student1
    ds.users[seeded_student2.user_id] = seeded_student2

    building = Building(building_id="bld001", building_name="LTB")
    other_building = Building(building_id="bld002", building_name="MTH")
    ds.buildings[building.building_id] = building
    ds.buildings[other_building.building_id] = other_building

    small_room = Room(
        room_id="rm001",
        room_name="LTB-101",
        building_id=building.building_id,
        room_type="Small",
    )
    medium_room = Room(
        room_id="rm002",
        room_name="MTH-201",
        building_id=other_building.building_id,
        room_type="Medium",
    )
    unavailable_room = Room(
        room_id="rm003",
        room_name="LTB-999",
        building_id=building.building_id,
        room_type="Small",
        is_available=False,
    )
    large_room = Room(
        room_id="rm004",
        room_name="MTH-301",
        building_id=other_building.building_id,
        room_type="Large",
    )
    ds.rooms[small_room.room_id] = small_room
    ds.rooms[medium_room.room_id] = medium_room
    ds.rooms[unavailable_room.room_id] = unavailable_room
    ds.rooms[large_room.room_id] = large_room

    projector = Equipment(
        equipment_id="eq001",
        room_id=small_room.room_id,
        equipment_type="Projector",
    )
    damaged_monitor = Equipment(
        equipment_id="eq002",
        room_id=small_room.room_id,
        equipment_type="Monitor",
        is_available=False,
        is_damaged=True,
    )
    other_projector = Equipment(
        equipment_id="eq003",
        room_id=medium_room.room_id,
        equipment_type="Projector",
    )
    ds.equipment[projector.equipment_id] = projector
    ds.equipment[damaged_monitor.equipment_id] = damaged_monitor
    ds.equipment[other_projector.equipment_id] = other_projector

    package = PackageDeal(
        package_id="pkg001",
        student_id=student.user_id,
        price=100.0,
        total_hours=12.0,
        remaining_hours=5.0,
    )
    ds.package_deals[package.package_id] = package

    return ds


def add_future_booking(ds, student, room_id="rm001", days=1,
                       start_time="10:00", end_time="12:00",
                       payment_method=Booking.PAYMENT_BALANCE,
                       total_cost=20.0):
    booking = Booking(
        booking_id=f"bk{len(ds.bookings) + 1:03d}",
        booking_reference=f"BR-TEST-{len(ds.bookings) + 1:03d}",
        student_id=student.user_id,
        room_id=room_id,
        date=future_date(days),
        start_time=start_time,
        end_time=end_time,
        duration=2.0,
        total_cost=total_cost,
        original_cost=total_cost,
        status=Booking.STATUS_ACTIVE,
        payment_method=payment_method,
    )
    ds.bookings[booking.booking_id] = booking
    return booking
