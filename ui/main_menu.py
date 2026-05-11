from ui.student_menu import StudentMenu
from ui.admin_menu import AdminMenu
from models.user import Student, Admin


class MainMenu:
    def __init__(self, data_service, auth_service):
        self.ds = data_service
        self.auth = auth_service
        self.student_menu = StudentMenu(data_service)
        self.admin_menu = AdminMenu(data_service)
        self.current_user = None

    def show(self):
        while True:
            print("\n" + "=" * 50)
            print("   Monash Smart Study Room Booking System (MSSRB)")
            print("=" * 50)
            print("  [1] Login")
            print("  [2] Register")
            print("  [0] Exit")
            print("-" * 50)
            choice = input(">> Enter your choice: ").strip()

            if choice == "1":
                self._login()
            elif choice == "2":
                self._register()
            elif choice == "0":
                print("\nThank you for using MSSRB. Goodbye!")
                break
            else:
                print("\n[!] Invalid option. Please try again.")

    def _login(self):
        print("\n" + "-" * 50)
        print("   Login")
        print("-" * 50)
        email = input(">> Email: ").strip()
        password = input(">> Password: ").strip()

        user, message = self.auth.login(email, password)
        if user is None:
            print(f"\n[!] {message}")
            return

        print(f"\n[+] {message}")
        self.current_user = user

        if isinstance(user, Student):
            self.student_menu.show(user)
        elif isinstance(user, Admin):
            self.admin_menu.show(user)

        self.current_user = None

    def _register(self):
        print("\n" + "-" * 50)
        print("   Student Registration")
        print("-" * 50)
        email = input(">> Email (@student.monash.edu): ").strip()
        password = input(">> Password: ").strip()
        first_name = input(">> First Name: ").strip()
        last_name = input(">> Last Name: ").strip()
        student_id = input(">> Student ID: ").strip()
        mobile_number = input(">> Mobile Number: ").strip()

        success, result = self.auth.register(
            email, password, first_name, last_name, student_id, mobile_number
        )

        if success:
            student = result
            print(f"\n[+] Registration successful!")
            print(f"    Student ID: {student.student_id}")
            print(f"    Name: {student.first_name} {student.last_name}")
            print(f"    Email: {student.email}")
        else:
            print(f"\n[!] Registration failed:")
            for line in result.split("\n"):
                print(f"    - {line}")
