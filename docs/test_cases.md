# Test Cases

## Scope

This document covers the Sprint 3 QA layers for the current Python CLI implementation:

- Unit tests for each available service file under `services/`
- Integration tests across registration, login, payment, room, booking, equipment, and data persistence flows
- Manual acceptance tests mapped to user-facing behaviours
- Black-box final demo scenarios

Current branch note: there is no separate `package_deal_service.py` or `cancellation_service.py`. Package deal behaviour is tested through `payment_service`, and cancellation behaviour is tested through `booking_service`.

## Test Code Distribution

The test files are assigned in five fixed packages. The mapping below keeps the package sizes balanced while matching the previous Trello/code ownership as closely as possible.

| Member | Test Files | Lines | Related Previous Work |
|---|---|---:|---|
| Shangwen Yin | `tests/test_booking_cancellation_service.py` | 222 | `booking.py`, booking status lifecycle, Sprint management |
| Zhitao Chen | `tests/test_booking_service.py` | 205 | `booking_service.py`, booking rules, room/booking models |
| Zihao Fan | `tests/test_equipment_service.py`, `tests/test_payment_service.py` | 203 | `equipment_service.py`; payment/deposit interactions are connected to equipment borrowing |
| Jiandong Wang | `tests/test_auth_service.py`, `tests/test_data_service.py` | 182 | `auth_service.py`, `user.py`, `payment_service.py`, `admin_menu.py`; data persistence is shared support |
| Xinyu Chen | `tests/test_room_service.py` | 167 | `student_menu.py`, room details view, student-facing room browsing flow |

Shared helper files: `tests/helpers.py` and `tests/__init__.py` are shared testing infrastructure, so they are not counted as one member's main test package.

## Automated Unit And Integration Tests

Command used:

```bash
python3 -B -m unittest discover -s tests -p 'test_*_service.py' -v
```

Latest result:

```text
Ran 70 tests in 0.044s
OK
```

| Test ID | Test Type | Test File | Input / Steps | Expected Output | Actual Output | Pass/Fail |
|---|---|---|---|---|---|---|
| UT-AUTH-001 | Unit | `tests/test_auth_service.py` | Login with `alice@student.monash.edu` and correct password | User object returned with success message | Passed by unittest | Pass |
| UT-AUTH-002 | Unit | `tests/test_auth_service.py` | Login with unknown email | Login rejected with email-not-found message | Passed by unittest | Pass |
| UT-AUTH-003 | Unit | `tests/test_auth_service.py` | Login with wrong password | Login rejected with incorrect-password message | Passed by unittest | Pass |
| UT-AUTH-004 | Unit | `tests/test_auth_service.py` | Register valid Monash student email and valid password | New student saved and returned | Passed by unittest | Pass |
| UT-AUTH-005 | Unit | `tests/test_auth_service.py` | Register with missing fields and weak password | Validation errors returned; no save | Passed by unittest | Pass |
| UT-AUTH-006 | Unit | `tests/test_auth_service.py` | Register duplicate email | Registration rejected | Passed by unittest | Pass |
| UT-AUTH-007 | Unit | `tests/test_auth_service.py` | Login with Trello-required seeded `student1` and `student2` accounts | Both return Student objects and success messages | Passed by unittest | Pass |
| UT-AUTH-008 | Unit | `tests/test_auth_service.py` | Add a new strike after a ban end date has already expired | Expired ban clears and the new strike starts a fresh count | Passed by unittest | Pass |
| UT-PAY-001 | Unit | `tests/test_payment_service.py` | Top up `$50.25` | Balance increases and top-up transaction created | Passed by unittest | Pass |
| UT-PAY-002 | Unit | `tests/test_payment_service.py` | Top up with `abc` | Input rejected | Passed by unittest | Pass |
| UT-PAY-003 | Unit | `tests/test_payment_service.py` | Top up `0`, `0.001`, and negative amount | Input rejected | Passed by unittest | Pass |
| UT-PAY-004 | Unit | `tests/test_payment_service.py` | Top up `1000.01` | Maximum amount error returned | Passed by unittest | Pass |
| UT-PAY-005 | Unit | `tests/test_payment_service.py` | Top up `nan` or `inf` | Input rejected without corrupting balance | Passed by unittest | Pass |
| UT-PAY-006 | Unit | `tests/test_payment_service.py` | Purchase package deal with enough balance | `$100` deducted and `12` package hours added | Passed by unittest | Pass |
| UT-PAY-007 | Unit | `tests/test_payment_service.py` | Purchase package deal with insufficient balance | Purchase rejected | Passed by unittest | Pass |
| UT-ROOM-001 | Unit | `tests/test_room_service.py` | Browse rooms | Only available rooms returned | Passed by unittest | Pass |
| UT-ROOM-002 | Unit | `tests/test_room_service.py` | Create room with valid building and room type | Room created with default type rules and saved | Passed by unittest | Pass |
| UT-ROOM-003 | Unit | `tests/test_room_service.py` | Create duplicate room in same building | Creation rejected | Passed by unittest | Pass |
| UT-ROOM-004 | Unit | `tests/test_room_service.py` | Create room with invalid capacity | Creation rejected | Passed by unittest | Pass |
| UT-ROOM-005 | Unit | `tests/test_room_service.py` | Create room with blank or whitespace-only room name | Creation rejected and no save occurs | Passed by unittest | Pass |
| UT-ROOM-006 | Unit | `tests/test_room_service.py` | Create room with blank or whitespace-only building name | Creation rejected and no blank building is created | Passed by unittest | Pass |
| UT-ROOM-007 | Unit | `tests/test_room_service.py` | Update name, building, capacity, and availability | Room fields updated | Passed by unittest | Pass |
| UT-ROOM-008 | Unit | `tests/test_room_service.py` | Remove room with active/future booking | Room is marked unavailable instead of deleted | Passed by unittest | Pass |
| UT-ROOM-009 | Unit | `tests/test_room_service.py` | Filter by party size `4` | Medium room whose range includes `4` is returned | Passed by unittest | Pass |
| UT-ROOM-010 | Unit | `tests/test_room_service.py` | Filter by overlapping time | Conflicting room excluded | Passed by unittest | Pass |
| UT-ROOM-011 | Unit | `tests/test_room_service.py` | Filter with non-padded time `9:00` | Datetime comparison still detects conflict | Passed by unittest | Pass |
| UT-ROOM-012 | Unit | `tests/test_room_service.py` | Get room details | Building and equipment breakdown returned | Passed by unittest | Pass |
| UT-ROOM-013 | Unit | `tests/test_room_service.py` | Update room with capacity `0`, `-1`, or `abc` | Update rejected and existing capacity unchanged | Passed by unittest | Pass |
| UT-ROOM-014 | Unit | `tests/test_room_service.py` | Filter outside updated opening hours | Room is excluded from availability results | Passed by unittest | Pass |
| UT-ROOM-015 | Unit | `tests/test_room_service.py` | Update room with invalid opening time | Update rejected and old opening time preserved | Passed by unittest | Pass |
| UT-BOOK-001 | Unit | `tests/test_booking_service.py` | Validate valid `09:30-10:00` slot | Valid with `0.5` hour duration | Passed by unittest | Pass |
| UT-BOOK-002 | Unit | `tests/test_booking_service.py` | Invalid date and short duration | Validation errors returned | Passed by unittest | Pass |
| UT-BOOK-003 | Unit | `tests/test_booking_service.py` | `09:15-10:15` | Rejected because not 30-minute increment | Passed by unittest | Pass |
| UT-BOOK-004 | Unit | `tests/test_booking_service.py` | Past booking start time | Rejected | Passed by unittest | Pass |
| UT-BOOK-005 | Unit | `tests/test_booking_service.py` | Banned student checkout | Checkout rejected | Passed by unittest | Pass |
| UT-BOOK-006 | Unit | `tests/test_booking_service.py` | Checkout using account balance | Booking and payment transaction created | Passed by unittest | Pass |
| UT-BOOK-007 | Unit | `tests/test_booking_service.py` | Checkout with insufficient balance | Checkout rejected | Passed by unittest | Pass |
| UT-BOOK-008 | Unit | `tests/test_booking_service.py` | Checkout with room conflict | Checkout rejected | Passed by unittest | Pass |
| UT-BOOK-009 | Unit | `tests/test_booking_service.py` | Student already has 3 future bookings | Checkout rejected | Passed by unittest | Pass |
| UT-BOOK-010 | Unit | `tests/test_booking_service.py` | First booking with `NEWBIE20` | 20% discount applied and promo marked used | Passed by unittest | Pass |
| UT-BOOK-011 | Unit | `tests/test_booking_service.py` | Reuse `NEWBIE20` | Promo rejected | Passed by unittest | Pass |
| UT-BOOK-012 | Unit | `tests/test_booking_service.py` | Checkout using package hours | Package hours deducted, balance unchanged | Passed by unittest | Pass |
| UT-BOOK-013 | Unit | `tests/test_booking_service.py` | Package hours insufficient | Checkout rejected | Passed by unittest | Pass |
| UT-BOOK-014 | Unit | `tests/test_booking_cancellation_service.py` | Cancel account-balance booking | Booking cancelled and balance refunded | Passed by unittest | Pass |
| UT-BOOK-015 | Unit | `tests/test_booking_cancellation_service.py` | Cancel package-hours booking | Booking cancelled and package hours restored | Passed by unittest | Pass |
| UT-BOOK-016 | Unit | `tests/test_booking_cancellation_service.py` | Late cancellation within 30 minutes | Strike added and refund processed | Passed by unittest | Pass |
| UT-BOOK-017 | Unit | `tests/test_booking_cancellation_service.py` | Admin marks past booking no-show | Status set to `NoShow` and strike added | Passed by unittest | Pass |
| UT-BOOK-018 | Unit | `tests/test_booking_cancellation_service.py` | Booking already started but not ended | Not treated as future | Passed by unittest | Pass |
| UT-BOOK-019 | Unit | `tests/test_booking_service.py` | Try `NEWBIE20` with package-hours payment | Checkout rejected and promo is not consumed | Passed by unittest | Pass |
| UT-BOOK-020 | Unit | `tests/test_booking_cancellation_service.py` | Cancel a discounted account-balance booking | Refund equals actual paid amount, not pre-discount price | Passed by unittest | Pass |
| UT-BOOK-021 | Unit | `tests/test_booking_cancellation_service.py` | Ended active booking has a returned equipment loan | Automated no-show detection leaves booking active | Passed by unittest | Pass |
| UT-BOOK-022 | Unit | `tests/test_booking_cancellation_service.py` | Admin marks ended booking with equipment loan as no-show | Marking is rejected | Passed by unittest | Pass |
| UT-BOOK-023 | Unit | `tests/test_booking_cancellation_service.py` | Get overdue bookings when ended booking has equipment loan | Booking is excluded from no-show review list | Passed by unittest | Pass |
| UT-BOOK-024 | Unit | `tests/test_booking_service.py` | Medium/Large booking violates duration or advance notice rules | Checkout rejected with room-specific validation | Passed by unittest | Pass |
| UT-BOOK-025 | Unit | `tests/test_booking_service.py` | Package-hours checkout for Medium room | Checkout rejected and package hours unchanged | Passed by unittest | Pass |
| UT-BOOK-026 | Unit | `tests/test_booking_service.py` | `NEWBIE20` checkout for Medium room | Promo rejected and usage not saved | Passed by unittest | Pass |
| UT-BOOK-027 | Unit | `tests/test_booking_cancellation_service.py` | Late Large room cancellation | 30% refund and one strike applied | Passed by unittest | Pass |
| UT-EQ-001 | Unit | `tests/test_equipment_service.py` | Get available equipment for room | Damaged/unavailable equipment excluded | Passed by unittest | Pass |
| UT-EQ-002 | Unit | `tests/test_equipment_service.py` | Borrow without valid active booking | Borrow rejected | Passed by unittest | Pass |
| UT-EQ-003 | Unit | `tests/test_equipment_service.py` | Borrow equipment during active booking | Deposit deducted, loan created, equipment unavailable | Passed by unittest | Pass |
| UT-EQ-004 | Unit | `tests/test_equipment_service.py` | Borrow with insufficient deposit | Borrow rejected | Passed by unittest | Pass |
| UT-EQ-005 | Unit | `tests/test_equipment_service.py` | Borrow equipment from a different room | Borrow rejected | Passed by unittest | Pass |
| UT-EQ-006 | Unit | `tests/test_equipment_service.py` | Return undamaged equipment | Deposit refunded and equipment available | Passed by unittest | Pass |
| UT-EQ-007 | Unit | `tests/test_equipment_service.py` | Return damaged equipment | Deposit forfeited and equipment marked damaged | Passed by unittest | Pass |
| INT-DATA-001 | Integration | `tests/test_data_service.py` | Start with empty temp data directory | Mock users, rooms, bookings, seed prices, and helpers initialized | Passed by unittest | Pass |
| INT-DATA-002 | Integration | `tests/test_data_service.py` | Save and reload CSV data | Student balance, room count, and room type defaults preserved | Passed by unittest | Pass |
| INT-DATA-003 | Integration | `tests/test_data_service.py` | Deduct and restore package hours | Package hours mutate correctly | Passed by unittest | Pass |
| INT-DATA-004 | Integration | `tests/test_data_service.py` | Simulate CSV read failure | Warning is produced and empty rows are returned without crashing | Passed by unittest | Pass |
| INT-DATA-005 | Integration | `tests/test_data_service.py` | Simulate CSV write failure | Warning is produced without crashing | Passed by unittest | Pass |
| INT-FLOW-001 | Integration | Multiple service tests | Register then login | Registered account can be located and authenticated | Covered by auth tests | Pass |
| INT-FLOW-002 | Integration | Multiple service tests | Login-like student object then top up | Balance and transaction history update | Covered by payment tests | Pass |
| INT-FLOW-003 | Integration | Multiple service tests | Browse room, book room, pay by balance/package | Booking service records booking and payment effects | Covered by room and booking tests | Pass |
| INT-FLOW-004 | Integration | Multiple service tests | Active booking then borrow/return equipment | Equipment loan and deposit lifecycle works | Covered by equipment tests | Pass |

## Manual Acceptance Test Cases

| Test ID | Test Type | Input / Steps | Expected Output | Actual Output | Pass/Fail |
|---|---|---|---|---|---|
| AT-001 | Acceptance | Student logs in with valid email/password | Student dashboard opens | Verified by automated auth login test | Pass |
| AT-002 | Acceptance | Student logs in with wrong password | Error message shown, no dashboard | Verified by automated auth login test | Pass |
| AT-003 | Acceptance | Student registers with invalid email and weak password | Form validation errors shown | Verified by automated register validation test | Pass |
| AT-004 | Acceptance | Student tops up valid amount | Balance increases and transaction stored | Verified by automated payment test | Pass |
| AT-005 | Acceptance | Student tops up non-number, negative, zero, too small, too large, NaN, infinity | Input rejected without balance corruption | Verified by automated payment tests | Pass |
| AT-006 | Acceptance | Student browses available rooms | Unavailable room not shown | Verified by automated room browse test | Pass |
| AT-007 | Acceptance | Admin updates room details | Updated room is stored and visible through service | Verified by automated room update test | Pass |
| AT-008 | Acceptance | Student books available room and pays by account balance | Booking confirmed, balance decreases | Verified by automated booking checkout test | Pass |
| AT-009 | Acceptance | Student books with conflicting room/time | Booking rejected | Verified by automated conflict tests | Pass |
| AT-010 | Acceptance | Student reaches 3 future bookings then tries a fourth | Booking rejected | Verified by automated booking limit test | Pass |
| AT-011 | Acceptance | First-time student uses `NEWBIE20` | 20% discount applied | Verified by automated promo test | Pass |
| AT-012 | Acceptance | Student tries to reuse `NEWBIE20` | Promo rejected | Verified by automated promo test | Pass |
| AT-013 | Acceptance | Student books using package hours | Hours deducted and cash balance unchanged | Verified by automated package-hours booking test | Pass |
| AT-014 | Acceptance | Student cancels account-balance booking before start | Refund issued | Verified by automated cancellation test | Pass |
| AT-015 | Acceptance | Student cancels package-hours booking before start | Package hours restored | Verified by automated cancellation test | Pass |
| AT-016 | Acceptance | Student cancels within 30 minutes | Late cancellation strike added | Verified by automated late cancellation test | Pass |
| AT-017 | Acceptance | Admin marks ended active booking no-show | No-show strike added | Verified by automated no-show test | Pass |
| AT-018 | Acceptance | Student borrows equipment during active booking | Deposit deducted and loan recorded | Verified by automated equipment test | Pass |
| AT-019 | Acceptance | Student returns equipment undamaged | Deposit refunded | Verified by automated equipment return test | Pass |
| AT-020 | Acceptance | Student returns equipment damaged | Deposit forfeited and equipment marked damaged | Verified by automated damaged return test | Pass |
| AT-021 | Acceptance | Medium/large room booking restriction | Duration and advance-notice violations are rejected | Verified by automated booking room-rule tests | Pass |
| AT-022 | Acceptance | Package can only be used for small room | Package-hours payment is rejected for Medium/Large rooms | Verified by automated package eligibility test | Pass |
| AT-023 | Acceptance | Student uses `NEWBIE20`, cancels booking, and checks balance | Balance returns to pre-booking amount after refunding actual paid amount | Verified by CLI black-box regression | Pass |
| AT-024 | Acceptance | Student tries `NEWBIE20` while paying with package hours | Checkout rejected and package hours remain unchanged | Verified by CLI black-box regression | Pass |
| AT-025 | Acceptance | Admin views rooms before update/remove | Room ID is visible in the room list | Verified by CLI black-box regression | Pass |
| AT-026 | Acceptance | Admin updates capacity with `abc` | Validation error shown; room is not saved as updated | Verified by CLI black-box regression | Pass |
| AT-027 | Acceptance | Student borrows and returns equipment, then admin reviews no-show list | Booking is not listed as no-show candidate | Verified by CLI black-box regression | Pass |
| AT-028 | Acceptance | Student uses `NEWBIE20` on Medium/Large room | Promo rejected and usage is not saved | Verified by automated promo room-type test | Pass |
| AT-029 | Acceptance | Admin updates opening/closing time | Availability filter excludes rooms outside updated hours | Verified by automated room opening-hour test | Pass |
| AT-030 | Acceptance | Clean mock data includes `student1@student.monash.edu`, `student2@student.monash.edu`, and `admin@monash.edu` | Required Trello demo accounts can log in | Verified by automated auth/data tests and direct local check | Pass |
| AT-031 | Acceptance | Inspect `.gitignore` for runtime data rules | `data/` is ignored | Verified by direct `.gitignore` check | Pass |

## Black-Box Final Demo Scenarios

| Test ID | Test Type | Input / Steps | Expected Output | Actual Output | Pass/Fail |
|---|---|---|---|---|---|
| BB-001 | Black-box | Register a new student, log in, top up, browse room, book with account balance | End-to-end student flow completes without crash | Covered by automated service integration and ready for final demo | Pass |
| BB-002 | Black-box | Admin creates/updates/removes room with invalid and valid inputs | Invalid input rejected; valid changes saved | Covered by automated room tests and ready for final demo | Pass |
| BB-003 | Black-box | Student attempts invalid booking time, conflict, and fourth future booking | All invalid bookings rejected with clear messages | Covered by automated booking tests and ready for final demo | Pass |
| BB-004 | Black-box | NEWBIE20 first use and reuse | First use discounted; reuse rejected | Covered by automated booking tests and ready for final demo | Pass |
| BB-005 | Black-box | Purchase package deal and book using package hours | Balance decreases by package price; package hours decrease on booking | Covered by automated payment and booking tests and ready for final demo | Pass |
| BB-006 | Black-box | Borrow equipment during active booking, return undamaged, then damaged | Deposit lifecycle behaves correctly | Covered by automated equipment tests and ready for final demo | Pass |
| BB-007 | Black-box | Enter malformed amount, malformed date/time, invalid capacity | Program returns validation messages and does not crash | Covered by automated service tests and ready for final demo | Pass |
| BB-008 | Black-box | Register student, top up, buy package, book with `NEWBIE20`, cancel, then inspect transactions | Booking payment `$16`, promo `$4`, refund `$16`, final balance unchanged from before booking | Executed through `python3 -B main.py` in an isolated data copy | Pass |
| BB-009 | Black-box | Register student, buy package, try package-hours booking with `NEWBIE20` | Error says promo can only be used with account balance; package hours remain `12.0` | Executed through `python3 -B main.py` in an isolated data copy | Pass |
| BB-010 | Black-box | Admin logs in, views rooms, then enters `abc` for capacity update | Room list includes Room ID; invalid capacity is rejected | Executed through `python3 -B main.py` in an isolated data copy | Pass |
| BB-011 | Black-box | Student borrows and returns equipment during an active session, then admin opens no-show review after session end | Deposit is refunded; returned-loan booking is not shown as overdue/no-show candidate | Executed through `python3 -B main.py` with an isolated active-session fixture | Pass |
