import re

from models.user import Student, Admin


class AuthService:
    def __init__(self, data_service):
        self.ds = data_service

    def register(self, email, password, first_name, last_name, student_id, mobile_number):
        # Validate all required fields with specific messages
        errors = []
        if not email or not email.strip():
            errors.append("Email is required.")
        elif not email.endswith("@student.monash.edu"):
            errors.append("Email must be a valid Monash student email (@student.monash.edu).")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        elif not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one number.")

        if not first_name or not first_name.strip():
            errors.append("First name is required.")
        if not last_name or not last_name.strip():
            errors.append("Last name is required.")
        if not student_id or not student_id.strip():
            errors.append("Student ID is required.")
        if not mobile_number or not mobile_number.strip():
            errors.append("Mobile number is required.")

        if errors:
            return False, "\n".join(errors)

        # Check duplicate email
        if self.ds.get_student_by_email(email.strip()):
            return False, "This email is already registered. Please log in instead."

        student = Student(
            email=email.strip(), password=password,
            first_name=first_name.strip(), last_name=last_name.strip(),
            student_id=student_id.strip(), mobile_number=mobile_number.strip(),
        )
        self.ds.users[student.user_id] = student
        self.ds.save_all()
        return True, student

    def login(self, email, password):
        user = self.ds.get_user_by_email(email.strip())
        if not user:
            return None, "Email not found. Please check your email or register."
        if user.password != password:
            return None, "Incorrect password. Please try again."
        return user, "Login successful."
