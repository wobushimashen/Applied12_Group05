# Monash Smart Study Room Booking System (MSSRB)

## 1. Project Overview
A terminal-based (CLI) study room booking system for Monash University students. Students can browse and filter study rooms, make bookings, pay with account balance or package hours, borrow equipment, and manage their accounts. Administrators can manage room inventory, update room details, and monitor bookings. The system is built with Python 3 using OOP principles and CSV file persistence.

## 2. Team Accountabilities
- Zihao Fan = Product Owner + Developer
- Shangwen Yin = Scrum Master + Developer
- Zhitao Chen = Developer
- Xinyu Chen = Developer
- Jiandong Wang = Developer

## 3. Main Features
| US | Feature | Description |
|----|---------|-------------|
| 1.1 | Registration | Student registration with Monash email validation |
| 1.2 | Add Funds | Top-up account balance ($0.01 - $1000) |
| 2.1 | Admin Room Management | Create, update, view, and remove/disable rooms |
| 2.2 | Equipment Borrowing | Borrow equipment with $100 deposit |
| 3.1 | Browse & Filter Rooms | Filter by time, building, and capacity |
| 3.2 | Cancel Booking | Cancellation with room-type late penalty tracking |
| 4.1 | Checkout & Payment | Pay with balance or package hours |
| 4.2 | Package Deal | $100 for 12 bookable hours for Small rooms only |
| 5.1 | No-Show Detection | Admin can mark no-shows and apply room-type penalties |
| 6.1 | Transaction History | View detailed transaction records |
| 7.1 | Room Details | View room type, equipment, price, and opening times |
| 8.1 | Admin Manage Bookings | Mark bookings as no-show |

## 4. Project Structure
```text
Applied12_Group05/
|-- main.py                    # Entry point
|-- models/                    # Entity classes (OOP)
|   |-- user.py                # User, Student, Admin
|   |-- building.py            # Building
|   |-- room.py                # Room and room-type rules
|   |-- equipment.py           # Equipment
|   |-- booking.py             # Booking
|   |-- equipment_loan.py      # EquipmentLoan
|   |-- package_deal.py        # PackageDeal
|   `-- transaction.py         # Transaction
|-- services/                  # Business logic
|   |-- data_service.py        # CSV read/write
|   |-- data_init.py           # Mock data + query helpers
|   |-- auth_service.py        # Registration, Login
|   |-- room_service.py        # Room CRUD, Browse/Filter
|   |-- booking_service.py     # Book, Cancel, Checkout, No-show
|   |-- equipment_service.py   # Borrow, Return, Damage
|   `-- payment_service.py     # Top-up, Package
|-- ui/                        # CLI menus
|   |-- main_menu.py           # Welcome, Login, Register
|   |-- student_menu.py        # Student dashboard
|   `-- admin_menu.py          # Admin dashboard
`-- data/                      # CSV data files, auto-created on first run
```

## 5. Data Files
All runtime data is stored in `data/` as CSV files:
- `users.csv` - Student and Admin accounts
- `buildings.csv` - Campus buildings
- `rooms.csv` - Study rooms, room types, standard equipment, prices, and opening times
- `equipment.csv` - Borrowable optional equipment
- `bookings.csv` - Room bookings
- `equipment_loans.csv` - Equipment loan records
- `package_deals.csv` - Purchased package deals
- `transactions.csv` - Financial transactions
- `promo_codes.csv` - Used promo codes

## 6. How to Run the Project
- **Language**: Python 3.13.x
- **IDE**: PyCharm (recommended)
- **Steps**:
  1. Open the project folder in PyCharm.
  2. Run `main.py`.
  3. Or from terminal: `python main.py`.

## 7. Sample Accounts
Primary testing accounts:

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

### Room Types, Prices, and Booking Rules
| Room Type | Capacity | Standard Equipment | Price/hr | Advance Notice | Min Duration | Late Cancellation | No-show |
|-----------|----------|--------------------|----------|----------------|--------------|-------------------|---------|
| Small | 1-2 | 1 table, 2 chairs | $10 | Any time | 0.5 hour | Within 0.5 hour: 50% forfeited, 50% refunded | 80% forfeited, 20% refunded |
| Medium | 3-6 | 1 big table, 6 chairs, 1 whiteboard on the wall | $40 | At least 3 hours | 2 hours | Within 3 hours: 50% refunded | 100% forfeited |
| Large | 5-10 | 1 meeting room table, 10 chairs, 1 built-in projector | $80 | At least 24 hours | 2 hours | Late cancellation: 30% refunded | 100% forfeited |

### Browse and Filter Rules
- Students can browse available rooms.
- Students can filter rooms by booking time, building, and capacity.
- Room details show room type, capacity, standard equipment, price per hour, opening time, closing time, availability, and optional equipment.

### Payment, Package Deal, and Promo Rules
- Account balance payment and package-hour payment are separate options; mixed payment is not supported.
- Package Deal costs `$100` and adds 12 bookable hours.
- Package hours can only be used for Small room bookings.
- Promo code `NEWBIE20` is only applicable to Small room bookings.
- `NEWBIE20` can only be used once per student and only for the student's first booking.

### Equipment Rules
- Optional equipment borrowing requires an active current booking.
- Borrowing optional equipment deducts a `$100` deposit.
- Returning equipment undamaged refunds the `$100` deposit.
- Returning equipment damaged forfeits the deposit.

### Admin Room Management Rules
- Admin can create rooms by room type: Small, Medium, or Large.
- Admin can update room name, building, capacity, standard equipment description, opening time, closing time, and availability.
- Updating standard equipment does not change the room price.
- Updating opening times affects future availability checks.
- Removing a room with future active bookings marks the room unavailable instead of deleting it.

## 9. How to Reset Data
- If `data/` is missing, the program auto-creates mock CSV data on first run.
- If old CSV data exists after schema or business-rule changes, delete the entire `data/` directory before running the program again.
- The program will recreate fresh mock CSV data on the next run.
- Terminal reset command from the project root:
  ```bash
  python -c "import shutil; from pathlib import Path; p=Path('data'); shutil.rmtree(p) if p.exists() else None"
  ```

## 10. Troubleshooting
- If old accounts or old room prices appear, delete `data/` and rerun `python main.py`.
- Ensure Python 3.13+ is installed and available as `python`.
- Run `python -m compileall .` to check for syntax/import errors.
- If a booking is unexpectedly rejected, check the room type, minimum duration, advance notice, opening hours, package-hour restrictions, and existing room conflicts.

## 11. Sprint 2 / 27 Apr Update Test Checklist
The local service-level smoke test should cover:
- `data/` regeneration and core CSV creation.
- Testing accounts: `student1`, `student2`, and `admin`.
- Small, Medium, and Large room data, including capacity, price, standard equipment, and opening times.
- Capacity filtering for Small, Medium, and Large rooms.
- Booking rules for Small 0.5h bookings, Medium/Large minimum duration, and Medium/Large advance notice.
- Package hours allowed for Small rooms only.
- `NEWBIE20` allowed for Small rooms only.
- Late cancellation refund rules for Small, Medium, and Large rooms.
- No-show forfeiture rules for Small, Medium, and Large rooms.

## 12. Contribution Summary
| Member | Role | Contributions |
|--------|------|---------------|
| Zihao Fan | Product Owner + Developer | Data persistence layer, Room service, Equipment service |
| Shangwen Yin | Scrum Master + Developer | Mock data initialization, Booking model, Sprint management |
| Zhitao Chen | Developer | Booking service, Login flow, Equipment loan model, Room model |
| Xinyu Chen | Developer | Student UI/CLI, Package deal, Room details view |
| Jiandong Wang | Developer | Admin UI/CLI, Auth service, Payment service, User model |
