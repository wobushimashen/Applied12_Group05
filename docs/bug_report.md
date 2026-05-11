# Bug Report

## Summary

Automated unit and integration testing was added for the available service layer. During test design, several edge-case bugs and requirement gaps were identified. Fixes listed as `pending commit` are implemented in the current working tree but have not yet been committed.

Verification command:

```bash
python3 -B -m unittest discover -s tests -p 'test_*_service.py' -v
```

Latest verification result:

```text
Ran 70 tests in 0.044s
OK
```

## Bugs Found

| Bug ID | Area | Severity | Status | Reproduction Steps | Expected Result | Actual Result Before Fix | Fix / Commit | Regression Test |
|---|---|---|---|---|---|---|---|---|
| BUG-001 | `PaymentService.add_funds` | Medium | Fixed in working tree | Call `add_funds(student, "nan")` or `"inf"` | Reject invalid amount and keep balance unchanged | Balance could become NaN/infinite because `float()` accepted those values | Added `math.isfinite()` validation; commit pending | `test_add_funds_rejects_nan_and_infinity` |
| BUG-002 | `PaymentService.add_funds` | Low | Fixed in working tree | Call `add_funds(student, "0.001")` | Reject amount below one cent | Accepted positive values smaller than `$0.01` | Changed minimum amount to `$0.01`; commit pending | `test_add_funds_rejects_zero_and_negative_amounts` |
| BUG-003 | `BookingService.validate_time_slot` | High | Fixed in working tree | Create booking with a past date/time | Booking should be rejected | Service accepted syntactically valid past times | Added future-start validation; commit pending | `test_validate_time_slot_rejects_past_start_time` |
| BUG-004 | `BookingService.checkout` | High | Fixed in working tree | Set student as banned, then call checkout directly | Checkout should be rejected | Direct service call did not check ban status | Added `student.can_make_booking()` guard; commit pending | `test_checkout_rejects_banned_student` |
| BUG-005 | `Booking.is_future` / cancellation | High | Fixed in working tree | Create booking that has started but not ended, then check `is_future()` | Started booking should not count as future | `is_future()` used end time, so active sessions could count as future | Changed `is_future()` to compare against start time; added `has_ended()` | `test_started_booking_is_not_future` |
| BUG-006 | Room conflict detection | High | Fixed in working tree | Existing booking `09:00-11:00`, request `9:00-10:00` | Conflict should be detected | String comparison could miss conflicts for non-padded time input | Changed conflict checks to parse datetimes | `test_filter_by_time_uses_datetime_not_string_order` |
| BUG-007 | `EquipmentService.borrow_equipment` | High | Fixed in working tree | Use active booking for room A to borrow equipment from room B | Borrow should be rejected | Service only checked active booking and equipment availability, not room match | Added equipment-room validation | `test_borrow_equipment_rejects_item_from_another_room` |
| BUG-008 | `BookingService.mark_no_show_admin` | Medium | Fixed in working tree | Mark an in-progress booking as no-show | Should reject until booking has ended | Future check alone was not precise enough | Added `Booking.has_ended()` and no-show end-time guard | `test_mark_no_show_admin_updates_status_and_strike` plus `test_started_booking_is_not_future` |
| BUG-009 | `RoomService.remove_room` | Medium | Fixed in working tree | Remove room with currently active booking | Room should remain in the system but be marked unavailable | Existing helper only considered future bookings and hard-rejected removal | Helper now checks future or active booking and marks the room unavailable | `test_remove_room_with_future_bookings_marks_unavailable` |
| BUG-010 | `RoomService.get_building_names` | Low | Fixed in working tree | Call `get_building_names()` for UI display | Building display names returned | Method returned building IDs | Return `building_name` values | `test_get_building_names_returns_display_names` |
| BUG-011 | `BookingService.cancel_booking` | High | Fixed in working tree | In CLI, first-time student books `$20` room with `NEWBIE20`, pays `$16`, then cancels | Refund should equal actual paid amount `$16` | System refunded original `$20`, increasing balance by `$4` | Refund account-balance bookings using `booking.total_cost`; commit pending | `test_cancel_booking_refunds_discounted_amount_only`; CLI regression `BB-008` |
| BUG-012 | `BookingService.checkout` | High | Fixed in working tree | In CLI, first-time student pays with package hours and enters `NEWBIE20` | Promo should not be consumed because no cash payment is discounted | Booking succeeded, package hours were deducted, and promo was marked used with no benefit | Reject `NEWBIE20` unless payment method is account balance; commit pending | `test_checkout_rejects_newbie20_with_package_hours`; CLI regression `BB-009` |
| BUG-013 | No-show review | High | Fixed in working tree | Student borrows and returns equipment during a session; admin reviews ended active bookings | Booking should not be listed or marked as no-show because attendance evidence exists | Returned loans were ignored, so the booking could be marked no-show | Treat any equipment loan for a booking as attendance evidence; commit pending | `test_no_show_detection_ignores_booking_with_returned_equipment_loan`, `test_mark_no_show_admin_rejects_booking_with_equipment_loan`, `test_overdue_bookings_exclude_booking_with_equipment_loan`; CLI regression `BB-011` |
| BUG-014 | `RoomService.update_room` | Medium | Fixed in working tree | Admin updates room capacity with `abc`, `0`, or `-1` | Input should be rejected and room should not be saved as updated | Invalid capacity was silently ignored and success was shown | Validate update capacity before mutating/saving room; commit pending | `test_update_room_rejects_invalid_capacity`; CLI regression `BB-010` |
| BUG-015 | Admin room CLI | Medium | Fixed in working tree | Admin views rooms, then update/remove asks for Room ID | Room ID should be visible in the room list | Room list only showed room name, building, capacity, price, and availability | Add `Room ID` column to admin room list; commit pending | CLI regression `BB-010` |
| BUG-016 | Room type rules | High | Fixed in working tree | Book Medium/Large room with too-short duration or too little advance notice | Medium/Large rules should reject invalid bookings | Room model had no room type, duration, advance-notice, opening-hour, or refund-rate fields | Added Small/Medium/Large defaults and enforced room rules in checkout and room filters; commit pending | `test_checkout_enforces_medium_and_large_room_rules`, `test_filter_by_time_excludes_rooms_outside_opening_hours` |
| BUG-017 | Package hours eligibility | High | Fixed in working tree | Use package hours to book Medium or Large room | Checkout should reject and package hours should remain unchanged | Package checkout only checked remaining package hours | Reject package-hours payment unless room type is `Small`; commit pending | `test_checkout_rejects_package_hours_for_non_small_rooms` |
| BUG-018 | `NEWBIE20` eligibility | Medium | Fixed in working tree | Use `NEWBIE20` on Medium or Large room | Promo should be rejected and usage should not be saved | Promo validation did not check room type | Reject `NEWBIE20` unless room type is `Small`; commit pending | `test_checkout_rejects_newbie20_for_non_small_rooms_without_saving_usage` |
| BUG-019 | Mock login accounts | High | Fixed in working tree | Log in with `student1@student.monash.edu / Student123!` or `student2@student.monash.edu / Student123!` after clean mock-data initialization | Both seeded accounts should authenticate successfully | Mock data only included named sample students such as Alice/Bob | Added the two Trello-required seeded student accounts to mock data and local runtime data; commit pending | `test_seeded_trello_student_accounts_can_login`, `test_initializes_mock_data_when_csv_files_are_missing` |
| BUG-020 | Runtime data tracking | Medium | Fixed in working tree | Inspect root `.gitignore` after runtime `data/` is generated | `data/` should be ignored and not committed | Root `.gitignore` did not ignore `data/` or Python bytecode | Added `data/`, `__pycache__/`, and `*.py[cod]` ignore rules; commit pending | Verified by direct `.gitignore` check |
| BUG-021 | CSV failure handling | Medium | Fixed in working tree | Simulate read/write `OSError` during CSV operations | CLI should show a graceful message and avoid crashing | CSV open/write errors propagated directly | Added guarded CSV read/write with warning messages; commit pending | `test_csv_read_failure_returns_empty_rows_without_crashing`, `test_csv_write_failure_does_not_crash` |
| BUG-022 | Mock booking and transaction data | Medium | Fixed in working tree | Initialize mock data or inspect existing runtime CSV after room-type pricing is enabled | Medium/Large booking costs and related transactions should match room pricing; package-hour bookings should use Small rooms | Some persisted and seeded rows still used old `$10/hour` values, and package-hour sample bookings pointed at Medium rooms | Corrected `services/data_init.py`, local `data/bookings.csv`, and local `data/transactions.csv`; commit pending | `test_initializes_mock_data_when_csv_files_are_missing` |
| BUG-025 | Admin no-show review redundant save | Low | Fixed in working tree | Choose `A` to mark all overdue bookings as no-show in admin booking review | Each mark operation should save once through `BookingService` | CLI performed an extra `save_all()` after service calls | Removed the redundant save; commit pending | Verified by full service test suite |
| BUG-026 | Admin booking menu unused import | Low | Fixed in working tree | Inspect `_manage_bookings()` implementation | No unused local import should remain | `Booking` was imported but not used | Removed the unused import; commit pending | Verified by `compileall` |
| BUG-028 | `Student.add_strike` expired-ban edge case | Low | Fixed in working tree | Call `add_strike()` for a student whose `is_banned=True` but `ban_end_date` is already past | Expired ban should be cleared before counting the new strike as a fresh cycle | Old strike counts could cause a new strike to restart a 90-day ban | Clear expired bans at the start of `add_strike()`; commit pending | `test_add_strike_clears_expired_ban_before_counting_new_violation` |
| BUG-029 / BUG-NEW-001 | `RoomService.create_room` | Medium | Fixed in working tree | Call `create_room("", "LTB")` or `create_room("   ", "LTB")` | Room creation should be rejected and no save should occur | Service accepted blank room names and created unnamed rooms | Trim and validate room name before building lookup or save; commit pending | `test_create_room_rejects_blank_room_name` |
| BUG-030 / BUG-NEW-002 | `RoomService.create_room` | Medium | Fixed in working tree | Call `create_room("TEST-101", "")` or whitespace building name | Room creation should be rejected and no building should be created | Service auto-created a building with a blank name | Trim and validate building name before auto-creating buildings; commit pending | `test_create_room_rejects_blank_building_name` |

## Reviewed False Positives

| Item | Reason Not Logged As Bug |
|---|---|
| BUG-023 persisted CSV dates are fixed calendar dates | This is expected once runtime CSV files exist. Deleting `data/` regenerates relative mock dates from `data_init.py`. |
| BUG-024 `validate_time_slot` malformed date handling | The existing `ValueError` branch already returns a clear format error, and the regression test covers it. |
| BUG-027 `_apply_booking_refund` unknown payment method variables | `refund_amount` and `restored_hours` are initialized before payment-method branching, so no `UnboundLocalError` occurs. |
| BUG-NEW-003 persisted CSV dates eventually age | Same category as BUG-023. Persisted runtime data should keep real calendar dates; clean mock data remains dynamic through `data_init.py`, and `data/` is ignored so stale local demo data is not committed. |

## Open Requirement Gaps

| Gap ID | Related Acceptance Criteria | Severity | Current Behaviour | Recommended Follow-up |
|---|---|---|---|---|
| GAP-001 | Separate `package_deal_service.py` and `cancellation_service.py` | Low | Logic exists inside `payment_service.py` and `booking_service.py` rather than separate service files | Keep current structure or refactor into separate service files if Sprint 3 architecture requires exact modules |

## Regression Result

All fixed bugs above are covered by automated regression tests in `tests/`.

```text
Ran 70 tests
OK
```
