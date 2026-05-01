from datetime import datetime, timedelta

from models.booking import Booking
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
        if duration_hours < 1:
            return False, "Minimum booking duration is 1 hour."

        # Check 30-minute increments
        if start.minute % 30 != 0 or end.minute % 30 != 0:
            return False, "Times must be in 30-minute increments (e.g., 09:00, 09:30)."

        return True, duration_hours

    def checkout(self, student, room_id, date, start_time, end_time,
                 payment_method, promo_code=None):
        # Check max 3 future bookings
        active_bookings = self.ds.get_active_future_bookings(student.user_id)
        if len(active_bookings) >= 3:
            return False, "You have reached the maximum of 3 future bookings. Please cancel an existing booking first."

        # Validate time
        valid, result = self.validate_time_slot(date, start_time, end_time)
        if not valid:
            return False, result
        duration = result

        # Check room exists and available
        room = self.ds.rooms.get(room_id)
        if not room:
            return False, "Room not found."
        if not room.is_available:
            return False, "This room is no longer available."

        # Re-check conflict at checkout time (AC: room becomes unavailable between selection and checkout)
        if self.ds.check_room_conflict(room_id, date, start_time, end_time):
            return False, "This room is no longer available for the selected time."

        total_cost = duration * room.price_per_hour

        # Apply promo code if provided
        discount = 0
        if promo_code and promo_code.strip().upper() == "NEWBIE20":
            if student.user_id in self.ds.promo_codes_used:
                return False, "This promo code has already been used."
            if len(self.ds.get_bookings_for_student(student.user_id)) > 0:
                return False, "Promo code NEWBIE20 is only valid for your first booking."
            discount = total_cost * 0.20

        final_cost = total_cost - discount
        original_cost = total_cost  # Track original cost for refund purposes

        # Process payment
        if payment_method == "1":  # Account balance
            if student.account_balance < final_cost:
                return False, "Insufficient funds. Please add funds to your account."
            student.account_balance -= final_cost
            pay_method = Booking.PAYMENT_BALANCE
        elif payment_method == "2":  # Package hours
            package_hours = self.ds.get_package_hours(student.user_id)
            if package_hours < duration:
                return False, "Insufficient package hours. Please purchase more hours or use account balance."
            self.ds.deduct_package_hours(student.user_id, duration)
            pay_method = Booking.PAYMENT_PACKAGE
            final_cost = 0  # No money deducted, hours used instead
        else:
            return False, "Invalid payment method."

        # Create booking
        booking = Booking(
            student_id=student.user_id,
            room_id=room_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_cost=final_cost if payment_method == "1" else duration * room.price_per_hour,
            original_cost=original_cost,
            status=Booking.STATUS_ACTIVE,
            payment_method=pay_method,
        )
        self.ds.bookings[booking.booking_id] = booking

        # Record transaction
        if payment_method == "1" and final_cost > 0:
            tx = Transaction(
                student_id=student.user_id,
                amount=final_cost,
                transaction_type=Transaction.TYPE_BOOKING_PAYMENT,
                description=f"Booking {booking.booking_reference} - {room.room_name}",
            )
            self.ds.transactions[tx.transaction_id] = tx

        # Mark promo code used
        if promo_code and promo_code.strip().upper() == "NEWBIE20" and discount > 0:
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

        # Determine cancellation type
        now = datetime.now()
        booking_start = datetime.strptime(f"{booking.date} {booking.start_time}",
                                          "%Y-%m-%d %H:%M")
        time_diff = (booking_start - now).total_seconds() / 60  # minutes

        is_late = time_diff <= 30

        # Update booking status
        booking.status = Booking.STATUS_CANCELLED

        # Process refund (refund original cost, not discounted cost)
        refund_amount = booking.original_cost
        if booking.payment_method == Booking.PAYMENT_BALANCE:
            student.account_balance += refund_amount
            tx = Transaction(
                student_id=student.user_id,
                amount=refund_amount,
                transaction_type=Transaction.TYPE_BOOKING_REFUND,
                description=f"Refund for cancelled booking {booking.booking_reference}",
            )
            self.ds.transactions[tx.transaction_id] = tx
        elif booking.payment_method == Booking.PAYMENT_PACKAGE:
            self.ds.restore_package_hours(student.user_id, booking.duration)
            refund_amount = 0  # Hours restored, not money

        if is_late:
            banned = student.add_strike("late_cancellation")
            total_strikes = student.late_cancellation_count + student.no_show_count
            self.ds.save_all()

            # Build detailed confirmation message per AC
            if booking.payment_method == Booking.PAYMENT_PACKAGE:
                refund_msg = f"Package hours ({booking.duration:.1f}) restored."
            else:
                refund_msg = f"Refund of ${refund_amount:.2f} processed."

            msg = (f"Late Cancellation recorded. {refund_msg}\n"
                   f"    Strikes: {total_strikes}/3. ")
            if banned:
                msg += f"You have been banned from booking until {student.ban_end_date}."
            else:
                msg += f"{3 - total_strikes} strikes remaining before a 3-month ban."
            return True, msg
        else:
            self.ds.save_all()
            if booking.payment_method == Booking.PAYMENT_PACKAGE:
                return True, (f"Booking {booking.booking_reference} cancelled. "
                              f"Package hours ({booking.duration:.1f}) restored.")
            else:
                return True, (f"Booking {booking.booking_reference} cancelled. "
                              f"Full refund of ${refund_amount:.2f} processed.")

    def mark_no_show(self, booking, student):
        booking.status = Booking.STATUS_NO_SHOW
        banned = student.add_strike("no_show")
        self.ds.save_all()
        return banned

    def get_student_bookings(self, student_id):
        return self.ds.get_bookings_for_student(student_id)

    def get_active_future_bookings(self, student_id):
        return self.ds.get_active_future_bookings(student_id)

    def get_cancellation_type(self, booking):
        """Determine if cancellation would be standard or late."""
        now = datetime.now()
        booking_start = datetime.strptime(f"{booking.date} {booking.start_time}",
                                          "%Y-%m-%d %H:%M")
        time_diff = (booking_start - now).total_seconds() / 60
        if time_diff > 30:
            return "Standard Cancellation"
        else:
            return "Late Cancellation"

    def check_no_shows(self):
        """Detect and mark bookings where the student did not show up.
        A booking is a no-show if: status is Active, end_time has passed,
        and no equipment was borrowed during the session.
        Returns list of (booking, student) tuples that were marked as no-show.
        """
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

            # Only check bookings that have ended
            if now <= booking_end:
                continue

            # Check if student borrowed equipment during this booking
            active_loans = [el for el in self.ds.equipment_loans.values()
                            if el.booking_id == booking.booking_id and not el.is_returned]
            if active_loans:
                continue  # Still has equipment, not a no-show

            # Mark as no-show
            student = self.ds.users.get(booking.student_id)
            if not student or not hasattr(student, 'add_strike'):
                continue

            booking.status = Booking.STATUS_NO_SHOW
            banned = student.add_strike("no_show")
            no_shows.append((booking, student, banned))

        if no_shows:
            self.ds.save_all()

        return no_shows

    def mark_no_show_admin(self, booking_id):
        """Admin manually marks a booking as no-show."""
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

        booking.status = Booking.STATUS_NO_SHOW
        banned = student.add_strike("no_show")
        total_strikes = student.late_cancellation_count + student.no_show_count
        self.ds.save_all()

        msg = f"Booking {booking.booking_reference} marked as No-Show. "
        msg += f"Strikes: {total_strikes}/3. "
        if banned:
            msg += f"Student banned until {student.ban_end_date}."
        return True, msg

    def get_all_bookings(self):
        return list(self.ds.bookings.values())

    def get_overdue_bookings(self):
        """Get active bookings that have passed their end time (potential no-shows)."""
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
