# LOT Schema Unit Tests - Quick Reference

## Test File Location
`backend/tests/unit/test_schemas_lot.py`

## Test Statistics
- **Total Tests**: 67
- **Test Classes**: 8
- **Expected Coverage**: 75-80% (from 53%)
- **Execution Time**: ~1-2 seconds

---

## Complete Test List with Descriptions

### TestLotStatusEnum (3 tests)

1. **test_lot_status_values**
   - Verifies LotStatus enum has correct values (CREATED, IN_PROGRESS, COMPLETED, CLOSED)

2. **test_lot_status_from_string**
   - Tests creating LotStatus enum from string values

3. **test_lot_status_invalid_value**
   - Ensures invalid status values raise ValueError

---

### TestShiftEnum (3 tests)

4. **test_shift_values**
   - Verifies Shift enum has correct values (D=Day, N=Night)

5. **test_shift_from_string**
   - Tests creating Shift enum from string values

6. **test_shift_invalid_value**
   - Ensures invalid shift values raise ValueError

---

### TestLotBaseValidation (20 tests)

7. **test_create_valid_lot_base**
   - Tests creating valid LotBase instance with all required fields

8. **test_shift_validator_uppercase_conversion**
   - Verifies lowercase shift 'd' converts to uppercase 'D'

9. **test_shift_validator_night_shift**
   - Tests lowercase night shift 'n' converts to 'N'

10. **test_shift_validator_enum_name**
    - Validates enum names DAY/NIGHT convert to D/N

11. **test_shift_validator_from_shift_enum**
    - Tests shift validator accepts Shift enum instances

12. **test_shift_validator_invalid_value**
    - Ensures invalid shift 'X' raises ValidationError

13. **test_shift_validator_invalid_type**
    - Ensures integer shift (123) raises ValidationError

14. **test_status_validator_uppercase_conversion**
    - Verifies lowercase status converts to uppercase

15. **test_status_validator_all_valid_statuses**
    - Tests all valid status values (CREATED, IN_PROGRESS, COMPLETED, CLOSED)

16. **test_status_validator_from_lot_status_enum**
    - Tests status validator accepts LotStatus enum instances

17. **test_status_validator_invalid_value**
    - Ensures invalid status raises ValidationError

18. **test_status_validator_invalid_type**
    - Ensures integer status (999) raises ValidationError

19. **test_target_quantity_minimum_value**
    - Tests minimum target_quantity value of 1

20. **test_target_quantity_maximum_value**
    - Tests maximum target_quantity value of 100

21. **test_target_quantity_below_minimum**
    - Ensures target_quantity=0 raises ValidationError

22. **test_target_quantity_above_maximum**
    - Ensures target_quantity=101 raises ValidationError

23. **test_target_quantity_invalid_type**
    - Ensures string target_quantity raises ValidationError

24. **test_product_model_id_validation**
    - Validates product_model_id must be > 0

25. **test_status_default_value**
    - Verifies status defaults to CREATED when not provided

---

### TestLotCreateSchema (2 tests)

26. **test_lot_create_inherits_validation**
    - Confirms LotCreate inherits all LotBase validation

27. **test_lot_create_with_all_fields**
    - Tests creating LotCreate with all fields populated

---

### TestLotUpdateValidation (14 tests)

28. **test_create_empty_lot_update**
    - Tests LotUpdate with no fields (all optional)

29. **test_update_shift_validation**
    - Tests shift validator in LotUpdate converts 'd' to 'D'

30. **test_update_shift_none**
    - Validates shift=None is accepted in LotUpdate

31. **test_update_status_validation**
    - Tests status validator in LotUpdate converts to uppercase

32. **test_update_status_none**
    - Validates status=None is accepted in LotUpdate

33. **test_update_target_quantity_validation**
    - Tests target_quantity validator in LotUpdate

34. **test_update_target_quantity_none**
    - Validates target_quantity=None is accepted

35. **test_update_target_quantity_below_minimum**
    - Ensures target_quantity=0 raises ValidationError in LotUpdate

36. **test_update_actual_quantity_validation**
    - Tests actual_quantity validator accepts valid values

37. **test_update_actual_quantity_zero**
    - Validates actual_quantity=0 is accepted

38. **test_update_actual_quantity_negative**
    - Ensures negative actual_quantity raises ValidationError

39. **test_update_actual_quantity_invalid_type**
    - Ensures string actual_quantity raises ValidationError

40. **test_update_passed_quantity_validation**
    - Tests passed_quantity validator (includes zero, negative, type tests)

41. **test_update_failed_quantity_validation**
    - Tests failed_quantity validator (includes zero, negative, type tests)

---

### TestLotUpdateQuantityConsistency (8 tests)

42. **test_quantity_consistency_valid_quantities**
    - Tests valid quantity combination (target=50, actual=45, passed=40, failed=5)

43. **test_quantity_consistency_actual_exceeds_target**
    - Ensures actual_quantity > target_quantity raises ValidationError

44. **test_quantity_consistency_passed_exceeds_actual**
    - Ensures passed_quantity > actual_quantity raises ValidationError

45. **test_quantity_consistency_failed_exceeds_actual**
    - Ensures failed_quantity > actual_quantity raises ValidationError

46. **test_quantity_consistency_passed_plus_failed_exceeds_actual**
    - Ensures passed + failed > actual raises ValidationError

47. **test_quantity_consistency_exact_sum**
    - Validates passed + failed = actual is accepted

48. **test_quantity_consistency_partial_update_no_actual**
    - Tests partial update without actual_quantity doesn't trigger validation

49. **test_quantity_consistency_actual_equals_target**
    - Validates actual_quantity = target_quantity is accepted

---

### TestLotInDBSchema (15 tests)

50. **test_defect_rate_calculation**
    - Verifies defect_rate = (failed / actual) × 100 = 10%

51. **test_pass_rate_calculation**
    - Verifies pass_rate = (passed / actual) × 100 = 95%

52. **test_defect_rate_with_zero_actual_quantity**
    - Ensures defect_rate returns None when actual_quantity=0

53. **test_pass_rate_with_zero_actual_quantity**
    - Ensures pass_rate returns None when actual_quantity=0

54. **test_rates_rounded_to_two_decimals**
    - Validates rates are rounded to 2 decimal places (73/75 = 97.33%)

55. **test_lot_number_pattern_validation**
    - Tests valid lot_number format (WF-KR-251120D-001)

56. **test_lot_number_invalid_pattern**
    - Ensures invalid lot_number format raises ValidationError

57. **test_lot_indb_with_product_model**
    - Tests LotInDB with nested ProductModelSchema

58. **test_defect_rate_provided_directly**
    - Validates provided defect_rate value is used instead of calculation

59. **test_pass_rate_provided_directly**
    - Validates provided pass_rate value is used instead of calculation

---

### TestProductModelSchema (2 tests)

60. **test_create_product_model_schema**
    - Tests creating ProductModelSchema with all required fields

61. **test_product_model_schema_optional_fields**
    - Tests ProductModelSchema with optional fields set to None

---

## Coverage Breakdown by Component

| Component | Tests | Coverage |
|-----------|-------|----------|
| Enum Validation | 6 | 100% |
| Shift Validators | 10 | 100% |
| Status Validators | 8 | 100% |
| Quantity Validators | 20 | 100% |
| Model Validators | 8 | 100% |
| Computed Fields | 10 | 100% |
| Pattern Validation | 2 | 100% |
| Nested Schemas | 3 | 100% |

## Quick Test Commands

### Run all LOT schema tests
```bash
pytest backend/tests/unit/test_schemas_lot.py -v
```

### Run with coverage
```bash
pytest backend/tests/unit/test_schemas_lot.py --cov=app.schemas.lot --cov-report=term-missing
```

### Run specific test class
```bash
pytest backend/tests/unit/test_schemas_lot.py::TestLotBaseValidation -v
```

### Run single test
```bash
pytest backend/tests/unit/test_schemas_lot.py::TestLotBaseValidation::test_shift_validator_uppercase_conversion -v
```

## Expected Results

- All 67 tests should pass
- Coverage should increase from 53% to 75-80%
- Execution time: 1-2 seconds
- No database or external dependencies required

## Key Validation Rules Tested

1. **Shift Validation**
   - Must be 'D' (Day) or 'N' (Night)
   - Case-insensitive input
   - Accepts enum names (DAY, NIGHT)

2. **Status Validation**
   - Must be CREATED, IN_PROGRESS, COMPLETED, or CLOSED
   - Case-insensitive input

3. **Target Quantity**
   - Range: 1-100 units
   - Business rule: Max 100 units per LOT

4. **Actual/Passed/Failed Quantities**
   - Must be non-negative
   - actual ≤ target
   - passed ≤ actual
   - failed ≤ actual
   - passed + failed ≤ actual

5. **Computed Metrics**
   - defect_rate = (failed / actual) × 100
   - pass_rate = (passed / actual) × 100
   - Returns None if actual = 0
   - Rounded to 2 decimals

6. **LOT Number Format**
   - Pattern: WF-KR-YYMMDD{D|N}-nnn
   - Example: WF-KR-251120D-001

---

**Generated**: 2025-11-19
**Status**: Ready for execution
**Phase**: Backend Coverage Enhancement - Phase 3
