# Monash Smart Study Room Booking System (MSSRB)

## 1. Project Overview
A terminal-based (CLI) study room booking system for Monash University students. Students can browse rooms, make bookings, borrow equipment, and manage their accounts. Administrators can manage room inventory. Built with Python 3 using OOP principles and CSV file storage.

## 2. Team Accountabilities
- FanZiHao = Product Owner + Developer
- YinShangWen = Scrum Master + Developer
- ChenZhiTao = Developer
- ChenXinYu = Developer
- WangJiandong = Developer

## 3. Main Features
- Student Registration & Login
- Add Funds & Purchase Package Deal
- Browse and Filter Rooms (by time and building)
- Checkout and Payment (Account Balance or Package Hours)
- Cancel Booking (with late cancellation tracking)
- Admin Room Management (Create, Update, Remove)
- Equipment Borrowing & Return (with deposit system)

## 4. Project Structure
```
Applied12_Group05/
├── main.py                    # Entry point
├── models/                    # Entity classes (OOP)
│   ├── user.py               # User (abstract), Student, Admin
│   ├── building.py           # Building
│   ├── room.py               # Room
│   ├── equipment.py          # Equipment
│   ├── booking.py            # Booking
│   ├── equipment_loan.py     # EquipmentLoan
│   ├── package_deal.py       # PackageDeal
│   └── transaction.py        # Transaction
├── services/                  # Business logic
│   ├── data_service.py       # CSV read/write, mock data
│   ├── auth_service.py       # Registration, Login
│   ├── room_service.py       # Room CRUD, Browse/Filter
│   ├── booking_service.py    # Book, Cancel, Checkout
│   ├── equipment_service.py  # Borrow, Return, Damage
│   └── payment_service.py    # Top-up, Package, Promo
├── ui/                        # CLI menus
│   ├── main_menu.py          # Welcome, Login, Register
│   ├── student_menu.py       # Student dashboard
│   └── admin_menu.py         # Admin dashboard
└── data/                      # CSV data files (auto-created)
```

## 5. Data Files
All stored in `data/` directory as CSV files:
- `users.csv` - Student and Admin accounts
- `buildings.csv` - Campus buildings
- `rooms.csv` - Study rooms
- `equipment.csv` - Borrowable equipment
- `bookings.csv` - Room bookings
- `equipment_loans.csv` - Equipment loan records
- `package_deals.csv` - Purchased package deals
- `transactions.csv` - Financial transactions
- `promo_codes.csv` - Used promo codes

## 6. How to Run the Project
- **Language**: Python 3.13.x
- **IDE**: PyCharm (recommended)
- **Steps**:
  1. Open the project folder in PyCharm
  2. Run `main.py`
  3. Or from terminal: `python main.py`

## 7. Sample Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@monash.edu | Monash1234! |
| Student | alice@student.monash.edu | Monash1!a |
| Student | bob@student.monash.edu | Monash1!b |

## 8. Business Rules
- Only `@student.monash.edu` emails accepted for registration
- Password: minimum 8 characters, at least 1 uppercase letter, 1 number
- Room price: AUD $10/hour (fixed), includes table and chair
- Maximum 3 future bookings per student
- Equipment borrowing: AUD $100 refundable deposit (Projector, Whiteboard, Monitor)
- Package Deal: $100 for 12 bookable hours (no expiry, hours stack)
- Promo code NEWBIE20: 20% off first booking (new accounts only)
- Cancellation: >30 min before = full refund; <=30 min = late cancellation strike
- 3 combined strikes (late cancellation + no-show) = 3-month booking ban
- Ban restarts from new violation date if violated during ban period
- After ban expires, strike counts reset to 0
- No mixed payment: must choose Account Balance OR Package Hours

## 9. Troubleshooting
- If `data/` directory is missing, it will be auto-created with mock data on first run
- Delete all CSV files in `data/` to reset to initial mock data
- Ensure Python 3.13+ is installed

## 10. Contribution Summary
| Member | Role | Contributions |
|--------|------|---------------|
| FanZiHao | Product Owner + Developer | Requirements, Room Management |
| YinShangWen | Scrum Master + Developer | Sprint Planning, Booking System |
| ChenZhiTao | Developer | Authentication, Data Layer |
| ChenXinYu | Developer | Equipment, Payment System |
| WangJiandong | Developer | UI/CLI, Integration |
