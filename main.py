"""
Monash Smart Study Room Booking System (MSSRB)
Main entry point for the CLI application.

Usage: python main.py
"""

from services.data_service import DataService
from services.auth_service import AuthService
from ui.main_menu import MainMenu


def main():
    print("Initializing MSSRB system...")
    data_service = DataService()
    auth_service = AuthService(data_service)
    menu = MainMenu(data_service, auth_service)
    menu.show()


if __name__ == "__main__":
    main()
