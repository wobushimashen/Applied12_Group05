from datetime import datetime

from models.booking import Booking
from models.room import Room
from models.transaction import Transaction


class BookingService:
    def __init__(self, data_service):
        self.ds = data_service

    def validate_time_slot(self, date, start_time, end_time):
        try:
            start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return False, "Invalid date or time format. Use YYYY-MM-DD and HH:MM."

        if end <= start:
            return False, "End time must be after start time."

        duration_hours = (end - start).total_seconds() / 3600
        if duration_hours < 0.5:
            return False, "Minimum booking duration is 0.5 hour."

        if start.minute % 30 != 0 or end.minute % 30 != 0:
            return False, "Times must be in 30-minute increments (e.g., 09:00, 09:30)."

        return True, duration_hours

    def checkout(self, student, room_id, date, start_time, end_time,
                 payment_method, promo_code=None):
        active_bookings = self.ds.get_active_future_bookings(student.user_id)
        if len(active_bookings) >= 3:
            return False, "You have reached the maximum of 3 future bookings. Please cancel an existing booking first."

        valid, result = self.validate_time_slot(date, start_time, end_time)
        if not valid:
            return False, result
        duration = result

        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."
        if not room.is_available:
            return False, "This room is no longer available."

        room_rule_ok, room_rule_msg = self._validate_room_booking_rules(room, date, start_time, end_time, duration)
        if not room_rule_ok:
            return False, room_rule_msg

        if self.ds.check_room_conflict(room_id, date, start_time, end_time):
            return False, "This room is no longer available for the selected time."

        total_cost = duration * room.price_per_hour
        discount = 0
        promo_applied = False
        if promo_code:
            code = promo_code.strip().upper()
            if code != "NEWBIE20":
                return False, "Invalid promo code."
            if room.room_type != Room.TYPE_SMALL:
                return False, "Promo code NEWBIE20 is only applicable on small room bookings."
            if student.user_id in self.ds.promo_codes_used:
                return False, "This promo code has already been used."
            if len(self.ds.get_bookings_for_student(student.user_id)) > 0:
                return False, "Promo code NEWBIE20 is only valid for your first booking."
            discount = total_cost * 0.20
            promo_applied = True

        final_cost = total_cost - discount

        if payment_method == "1":
            if student.account_balance < final_cost:
                return False, "Insufficient funds. Please add funds to your account."
            student.account_balance -= final_cost
            pay_method = Booking.PAYMENT_BALANCE
        elif payment_method == "2":
            if room.room_type != Room.TYPE_SMALL:
                return False, "Package hours can ONLY be used for Small room bookings."
            package_hours = self.ds.get_package_hours(student.user_id)
            if package_hours < duration:
                return False, "Insufficient package hours. Please purchase more hours or use account balance."
            self.ds.deduct_package_hours(student.user_id, duration)
            pay_method = Booking.PAYMENT_PACKAGE
            final_cost = 0
        else:
            return False, "Invalid payment method."

        booking = Booking(
            student_id=student.user_id,
            room_id=room_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_cost=final_cost if payment_method == "1" else total_cost,
            original_cost=total_cost,
            status=Booking.STATUS_ACTIVE,
            payment_method=pay_method,
        )
        self.ds.bookings[booking.booking_id] = booking

        if payment_method == "1" and final_cost > 0:
            tx = Transaction(
                student_id=student.user_id,
                amount=final_cost,
                transaction_type=Transaction.TYPE_BOOKING_PAYMENT,
                description=f"Booking {booking.booking_reference} - {room.room_name}",
            )
            self.ds.transactions[tx.transaction_id] = tx

        if promo_applied:
            self.ds.promo_codes_used.add(student.user_id)
            tx_promo = Transaction(
                student_id=student.user_id,
                amount=discount,
                transaction_type=Transaction.TYPE_PROMO_DISCOUNT,
                description=f"NEWBIE20 discount on {booking.booking_reference}",
            )
            self.ds.transactions[tx_promo.transaction_id] = tx_promo

        self.ds.save_all()
        return True, booking

    def cancel_booking(self, student, booking_id):
        booking = self.ds.bookings.get(booking_id)
        if not booking:
            return False, "Booking not found."
        if booking.student_id != student.user_id:
            return False, "This booking does not belong to you."
        if booking.status != Booking.STATUS_ACTIVE:
            return False, "This booking is not active."
        if not booking.is_future():
            return False, "Cannot cancel a booking that has already started or ended."

        room = self.ds.rooms.get(booking.room_id)
        if not room:
            return False, "Room not found."

        now = datetime.now()
        booking_start = datetime.strptime(f"{booking.date} {booking.start_time}",
                                          "%Y-%m-%d %H:%M")
        hours_before_start = (booking_start - now).total_seconds() / 3600
        is_late = hours_before_start <= room.late_cancel_threshold_hours
        refund_rate = room.late_cancel_refund_rate if is_late else 1.0

        booking.status = Booking.STATUS_CANCELLED
        refund_msg = self._apply_refund(student, booking, refund_rate,
                                        f"Refund for cancelled booking {booking.booking_reference}")

        if is_late:
            banned = student.add_strike("late_cancellation")
            total_strikes = student.late_cancellation_count + student.no_show_count
            self.ds.save_all()
            msg = (f"Late Cancellation recorded for {room.room_type} room. {refund_msg}\n"
                   f"    Strikes: {total_strikes}/3. ")
            if banned:
                msg += f"You have been banned from booking until {student.ban_end_date}."
            else:
                msg += f"{3 - total_strikes} strikes remaining before a 3-month ban."
            return True, msg

        self.ds.save_all()
        return True, f"Booking {booking.booking_reference} cancelled. {refund_msg}"

    def mark_no_show(self, booking, student):
        return self._mark_no_show(booking, student)[0]

    def get_student_bookings(self, student_id):
        return self.ds.get_bookings_for_student(student_id)

    def get_active_future_bookings(self, student_id):
        return self.ds.get_active_future_bookings(student_id)

    def get_cancellation_type(self, booking):
        room = self.ds.rooms.get(booking.room_id)
        if not room:
            return "Unknown"
        now = datetime.now()
        booking_start = datetime.strptime(f"{booking.date} {booking.start_time}",
                                          "%Y-%m-%d %H:%M")
        hours_before_start = (booking_start - now).total_seconds() / 3600
        if hours_before_start <= room.late_cancel_threshold_hours:
            return "Late Cancellation"
        return "Standard Cancellation"

    def check_no_shows(self):
        now = datetime.now()
        no_shows = []

        for booking in list(self.ds.bookings.values()):
            if booking.status != Booking.STATUS_ACTIVE:
                continue

            try:
                booking_end = datetime.strptime(
                    f"{booking.date} {booking.end_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            if now <= booking_end:
                continue

            active_loans = [el for el in self.ds.equipment_loans.values()
                            if el.booking_id == booking.booking_id and not el.is_returned]
            if active_loans:
                continue

            student = self.ds.users.get(booking.student_id)
            if not student or not hasattr(student, 'add_strike'):
                continue

            ok, msg, banned = self._mark_no_show(booking, student)
            if ok:
                no_shows.append((booking, student, banned, msg))

        if no_shows:
            self.ds.save_all()

        return no_shows

    def mark_no_show_admin(self, booking_id):
        booking = self.ds.bookings.get(booking_id)
        if not booking:
            return False, "Booking not found."
        if booking.status != Booking.STATUS_ACTIVE:
            return False, "This booking is not active."
        if booking.is_future():
            return False, "Cannot mark a future booking as no-show."

        student = self.ds.users.get(booking.student_id)
        if not student or not hasattr(student, 'add_strike'):
            return False, "Student not found."

        ok, msg, _ = self._mark_no_show(booking, student)
        self.ds.save_all()
        return ok, msg

    def get_all_bookings(self):
        return list(self.ds.bookings.values())

    def get_overdue_bookings(self):
        now = datetime.now()
        overdue = []
        for b in self.ds.bookings.values():
            if b.status != Booking.STATUS_ACTIVE:
                continue
            try:
                end = datetime.strptime(f"{b.date} {b.end_time}", "%Y-%m-%d %H:%M")
                if now > end:
                    overdue.append(b)
            except ValueError:
                continue
        return overdue

    def _validate_room_booking_rules(self, room, date, start_time, end_time, duration):
        if duration < room.minimum_duration_hours:
            return False, (f"{room.room_type} rooms require a minimum booking duration "
                           f"of {room.minimum_duration_hours:.1f} hour(s).")

        if not (room.opening_time <= start_time and end_time <= room.closing_time):
            return False, (f"Room is open from {room.opening_time} to "
                           f"{room.closing_time}.")

        if room.advance_notice_hours > 0:
            start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            hours_until_start = (start - datetime.now()).total_seconds() / 3600
            if hours_until_start < room.advance_notice_hours:
                return False, (f"{room.room_type} rooms must be booked at least "
                               f"{room.advance_notice_hours:.0f} hours in advance.")

        return True, ""

    def _apply_refund(self, student, booking, refund_rate, description):
        if booking.payment_method == Booking.PAYMENT_PACKAGE:
            hours = booking.duration * refund_rate
            if hours > 0:
                self.ds.restore_package_hours(student.user_id, hours)
            return f"{hours:.1f} package hours restored."

        refund_amount = booking.total_cost * refund_rate
        if refund_amount > 0:
            student.account_balance += refund_amount
            tx = Transaction(
                student_id=student.user_id,
                amount=refund_amount,
                transaction_type=Transaction.TYPE_BOOKING_REFUND,
                description=description,
            )
            self.ds.transactions[tx.transaction_id] = tx
        return f"Refund of ${refund_amount:.2f} processed."

    def _mark_no_show(self, booking, student):
        room = self.ds.rooms.get(booking.room_id)
        if not room:
            return False, "Room not found.", False

        booking.status = Booking.STATUS_NO_SHOW
        banned = student.add_strike("no_show")
        refund_msg = self._apply_refund(
            student,
            booking,
            room.no_show_refund_rate,
            f"No-show refund for booking {booking.booking_reference}",
        )
        total_strikes = student.late_cancellation_count + student.no_show_count
        msg = (f"Booking {booking.booking_reference} marked as No-Show for "
               f"{room.room_type} room. {refund_msg} Strikes: {total_strikes}/3.")
        if banned:
            msg += f" Student banned until {student.ban_end_date}."
        return True, msg, banned
