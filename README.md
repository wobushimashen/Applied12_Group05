# Monash Smart Study Room Booking System (MSSRB)

## 1. Project Overview
A terminal-based (CLI) study room booking system for Monash University students. Students can browse rooms, make bookings, borrow equipment, and manage their accounts. Administrators can manage room inventory and monitor bookings. Built with Python 3 using OOP principles and CSV file storage.

## 2. Team Accountabilities
- Zihao Fan = Product Owner + Developer
- Shangwen Yin = Scrum Master + Developer
- Zhitao Chen = Developer
- Xinyu Chen = Developer
- Jiandong Wang = Developer

## 3. Main Features (12 User Stories)
| US | Feature | Description |
|----|---------|-------------|
| 1.1 | Registration | Student registration with Monash email validation |
| 1.2 | Add Funds | Top-up account balance ($0.01 - $1000) |
| 2.1 | Admin Room Management | Create, update, remove rooms |
| 2.2 | Equipment Borrowing | Borrow equipment with $100 deposit |
| 3.1 | Browse & Filter Rooms | Filter by time, building, capacity |
| 3.2 | Cancel Booking | Cancellation with late penalty tracking |
| 4.1 | Checkout & Payment | Pay with balance or package hours |
| 4.2 | Package Deal | $100 for 12 bookable hours |
| 5.1 | No-Show Detection | Auto-detect and penalize no-shows |
| 6.1 | Transaction History | View detailed transaction records |
| 7.1 | Room Details | View room info and available equipment |
| 8.1 | Admin Manage Bookings | Mark bookings as no-show |

## 4. Project Structure
```
Applied12_Group05/
├── main.py                    # Entry point
├── models/                    # Entity classes (OOP)
│   ├── __init__.py
│   ├── user.py               # User (abstract), Student, Admin
│   ├── building.py           # Building
│   ├── room.py               # Room
│   ├── equipment.py          # Equipment
│   ├── booking.py            # Booking
│   ├── equipment_loan.py     # EquipmentLoan
│   ├── package_deal.py       # PackageDeal
│   └── transaction.py        # Transaction
├── services/                  # Business logic
│   ├── __init__.py
│   ├── data_service.py       # CSV read/write
│   ├── data_init.py          # Mock data + query helpers
│   ├── auth_service.py       # Registration, Login
│   ├── room_service.py       # Room CRUD, Browse/Filter
│   ├── booking_service.py    # Book, Cancel, Checkout, No-show
│   ├── equipment_service.py  # Borrow, Return, Damage
│   └── payment_service.py    # Top-up, Package, Promo
├── ui/                        # CLI menus
│   ├── __init__.py
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
| Student | student1@student.monash.edu | Student123! |
| Student | student2@student.monash.edu | Student123! |
| Student | alice@student.monash.edu | Monash1!a |
| Student | bob@student.monash.edu | Monash1!b |
| Student | charlie@student.monash.edu | Monash1!c |
| Student | diana@student.monash.edu | Monash1!d |
| Student | ethan@student.monash.edu | Monash1!e |
| Student | fiona@student.monash.edu | Monash1!f |
| Student | george@student.monash.edu | Monash1!g |
| Student | hannah@student.monash.edu | Monash1!h |

## 8. Business Rules
- Only `@student.monash.edu` emails accepted for registration
- Password: minimum 8 characters, at least 1 uppercase letter, 1 number
- Room types: Small `1-2` people at `$10/hour`, Medium `3-6` people at `$40/hour`, Large `5-10` people at `$80/hour`
- Booking rules: Small minimum `0.5` hour, Medium/Large minimum `2` hours, Medium requires `3` hours advance notice, Large requires `24` hours advance notice
- Maximum 3 future bookings per student
- Equipment borrowing: AUD $100 refundable deposit (Projector, Whiteboard, Monitor)
- Package Deal: $100 for 12 bookable hours (Small rooms only; no expiry, hours stack)
- Promo code NEWBIE20: 20% off first Small-room booking with account balance (new accounts only)
- Cancellation: outside late window = full refund; late cancellation adds a strike and refunds Small/Medium 50%, Large 30%
- No-show refund: Small 20%, Medium/Large 0%
- 3 combined strikes (late cancellation + no-show) = 3-month booking ban
- Ban restarts from new violation date if violated during ban period
- After ban expires, strike counts reset to 0
- No mixed payment: must choose Account Balance OR Package Hours

## 9. Troubleshooting
- If `data/` directory is missing, it will be auto-created with mock data on first run
- Delete all CSV files in `data/` to reset to initial mock data
- Ensure Python 3.13+ is installed

## 10. Code File Distribution
| Member | Files | Lines |
|--------|-------|-------|
| Zihao Fan | data_service.py, room_service.py, equipment_service.py | 435 |
| Shangwen Yin | data_init.py, booking.py, __init__.py | 445 |
| Zhitao Chen | booking_service.py, main_menu.py, transaction.py, equipment_loan.py, room.py, equipment.py, building.py | 413 |
| Xinyu Chen | student_menu.py, package_deal.py | 473 |
| Jiandong Wang | admin_menu.py, payment_service.py, auth_service.py, user.py, main.py | 408 |
| **Total** | **20 Python files** | **2174** |

## 11. Contribution Summary
| Member | Role | Contributions |
|--------|------|---------------|
| Zihao Fan | Product Owner + Developer | Data persistence layer, Room service, Equipment service |
| Shangwen Yin | Scrum Master + Developer | Mock data initialization, Booking model, Sprint management |
| Zhitao Chen | Developer | Booking service, Login flow, Equipment loan model, Room model |
| Xinyu Chen | Developer | Student UI/CLI, Package deal, Room details view |
| Jiandong Wang | Developer | Admin UI/CLI, Auth service, Payment service, User model |
