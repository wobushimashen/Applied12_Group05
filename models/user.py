import uuid
from abc import ABC


class User(ABC):
    def __init__(self, user_id=None, email="", password="", first_name="", last_name=""):
        self.user_id = user_id or str(uuid.uuid4())[:8]
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }


class Student(User):
    def __init__(self, user_id=None, email="", password="", first_name="", last_name="",
                 student_id="", mobile_number="", account_balance=0.0,
                 is_banned=False, ban_end_date="",
                 late_cancellation_count=0, no_show_count=0):
        super().__init__(user_id, email, password, first_name, last_name)
        self.student_id = student_id
        self.mobile_number = mobile_number
        self.account_balance = float(account_balance)
        self.is_banned = is_banned
        self.ban_end_date = ban_end_date
        self.late_cancellation_count = int(late_cancellation_count)
        self.no_show_count = int(no_show_count)

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "role": "student",
            "student_id": self.student_id,
            "mobile_number": self.mobile_number,
            "account_balance": f"{self.account_balance:.2f}",
            "is_banned": str(self.is_banned),
            "ban_end_date": self.ban_end_date,
            "late_cancellation_count": str(self.late_cancellation_count),
            "no_show_count": str(self.no_show_count),
        })
        return d

    def _clear_expired_ban(self):
        from datetime import datetime

        if self.is_banned and self.ban_end_date:
            ban_end = datetime.strptime(self.ban_end_date, "%Y-%m-%d")
            if datetime.now() >= ban_end:
                self.is_banned = False
                self.ban_end_date = ""
                self.late_cancellation_count = 0
                self.no_show_count = 0

    def can_make_booking(self):
        from datetime import datetime

        self._clear_expired_ban()
        if self.is_banned and self.ban_end_date:
            ban_end = datetime.strptime(self.ban_end_date, "%Y-%m-%d")
            if datetime.now() < ban_end:
                return False
        return True

    def add_strike(self, strike_type):
        self._clear_expired_ban()

        if strike_type == "late_cancellation":
            self.late_cancellation_count += 1
        elif strike_type == "no_show":
            self.no_show_count += 1

        from datetime import datetime, timedelta
        total = self.late_cancellation_count + self.no_show_count

        if total >= 3:
            # If already banned, restart ban from now (per client requirement)
            self.is_banned = True
            self.ban_end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        elif self.is_banned and self.ban_end_date:
            # If banned and new violation but total < 3, still restart ban
            self.ban_end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")

        return self.is_banned


class Admin(User):
    def __init__(self, user_id=None, email="", password="", first_name="", last_name=""):
        super().__init__(user_id, email, password, first_name, last_name)

    def to_dict(self):
        d = super().to_dict()
        d["role"] = "admin"
        return d
