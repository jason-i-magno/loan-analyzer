from decimal import Decimal

import pytest
from loan_utils.dollar import Dollar


@pytest.fixture(
    params=[
        (
            Decimal(2.675)
        ),  # Disallow Decimal to prevent issues with floating point precision (e.g., Decimal(2.675) becomes Decimal(2.67499999999999999999999999))
        (None),  # Disallow None
        ([]),  # Disallow list
        ({}),  # Disallow dict
        (set()),  # Disallow set
        (object()),  # Disallow object
        ("abc"),  # Disallow non-numeric string
    ]
)
def invalid_case(request):
    return request.param


def test_dollar_copy_constructor():
    original: Dollar = Dollar(100)
    copy: Dollar = Dollar(original)

    assert copy.amount == original.amount
    assert copy is not original


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, 0.0),  # zero
        (0.004, 0.0),  # very small
        (0.005, 0.01),  # very small
        (1e20, 100000000000000000000.00),  # very large
        (100, 100.00),  # int
        (100.456, 100.46),  # float
        ("100.456", 100.46),  # str
        (-50.567, -50.57),  # negative float
        (123456789.987, 123456789.99),  # large float
        (0.004, 0.0),  # small float
        (2.675, 2.68),  # floating point precision
        ("2.675", 2.68),  # floating point precision str
    ],
)
def test_dollar_init_valid(input_value, expected):
    dollar = Dollar(input_value)

    assert dollar.amount == Decimal(str(expected))


def test_dollar_init_invalid(invalid_case):
    with pytest.raises(Exception):
        Dollar(invalid_case)


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, "$0.00"),  # zero
        (0.004, "$0.00"),  # very small
        (0.005, "$0.01"),  # very small
        (1e20, "$100,000,000,000,000,000,000.00"),  # very large
        (100, "$100.00"),  # 0 < int < 1000
        (1000, "$1,000.00"),  # 1,000 <= int < 1,000,000
        (1000000, "$1,000,000.00"),  # 1,000,000 <= int < 1,000,000,000
        (100.004, "$100.00"),  # 0 < float < 1000
        (1000.50, "$1,000.50"),  # 1,000 <= float < 1,000,000
        (1000000.75, "$1,000,000.75"),  # 1,000,000 <= float < 1,000,000,000
        ("100.00", "$100.00"),  # 0 < str < 1000
        ("1000.50", "$1,000.50"),  # 1,000 <= str < 1,000,000
        ("1000000.75", "$1,000,000.75"),  # 1,000,000 <= str < 1,000,000,000
        (-1000, "-$1,000.00"),  # negative int
        (-1000.50, "-$1,000.50"),  # negative float
        (-1000.75, "-$1,000.75"),  # negative str
        (2.675, "$2.68"),  # floating point precision
        ("2.675", "$2.68"),  # floating point precision str
    ],
)
def test_dollar_str(input_value, expected):
    dollar: Dollar = Dollar(input_value)

    assert str(dollar) == expected
    assert Dollar(str(dollar).replace("$", "").replace(",", "")) == dollar


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, "Dollar(0.00)"),  # zero
        (0.004, "Dollar(0.00)"),  # very small
        (0.005, "Dollar(0.01)"),  # very small
        (1e20, "Dollar(100000000000000000000.00)"),  # very large
        (100, "Dollar(100.00)"),  # int
        (100.5, "Dollar(100.50)"),  # float
        ("100.456", "Dollar(100.46)"),  # str
        (-50, "Dollar(-50.00)"),  # negative int
        (-50.567, "Dollar(-50.57)"),  # negative float
        ("-50.567", "Dollar(-50.57)"),  # negative str
        (2.675, "Dollar(2.68)"),  # floating point precision
        ("2.675", "Dollar(2.68)"),  # floating point precision str
    ],
)
def test_dollar_repr(input_value, expected):
    d = Dollar(input_value)
    assert repr(d) == expected
    # Optional: ensure eval(repr(d)) reconstructs equal Dollar
    reconstructed = eval(repr(d))
    assert isinstance(reconstructed, Dollar)
    assert reconstructed.amount == d.amount


# --------------------
# Arithmetic Operators
# --------------------
@pytest.fixture(
    params=[
        ([0, 0], 0.0),  # zero
        ([0.005, 0.0], 0.01),  # very small
        ([1e20, 2e20], 3e20),  # very large
        ([100, 50], 150.0),  # int
        ([100.5, 50.25], 150.75),  # float
        (["100.5", "50.25"], 150.75),  # str
        ([100, -50], 50.0),  # negative int
        ([100.5, -50.25], 50.25),  # negative float
        (["100.5", "-50.25"], 50.25),  # negative str
    ]
)
def valid_inputs_add(request):
    return request.param


def test_dollar_add_valid(valid_inputs_add):
    input_value, expected = valid_inputs_add
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 + dollar_2).amount == Decimal(str(expected))
    assert (dollar_1 + input_value[1]).amount == Decimal(str(expected))


def test_dollar_add_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar + invalid_case


def test_dollar_iadd_valid(valid_inputs_add):
    input_value, expected = valid_inputs_add
    dollar: Dollar = Dollar(input_value[0])
    dollar += Dollar(input_value[1])

    assert dollar.amount == Decimal(str(expected))

    dollar = Dollar(input_value[0])
    dollar += input_value[1]

    assert dollar.amount == Decimal(str(expected))


def test_dollar_iadd_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar += invalid_case


def test_dollar_radd_valid(valid_inputs_add):
    input_value, expected = valid_inputs_add
    dollar: Dollar = Dollar(input_value[1])

    assert (input_value[0] + dollar).amount == Decimal(str(expected))


def test_dollar_radd_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        invalid_case + dollar


@pytest.fixture(
    params=[
        ([0, 0], 0.0),  # zero
        ([0.005, 0.0], 0.01),  # very small
        ([2e20, 1e20], 1e20),  # very large
        ([100, 50], 50.0),  # int
        ([100.5, 50.25], 50.25),  # float
        (["100.5", "50.25"], 50.25),  # str
        ([100, -50], 150.0),  # negative int
        ([100.5, -50.25], 150.75),  # negative float
        (["100.5", "-50.25"], 150.75),  # negative str
    ]
)
def valid_inputs_sub(request):
    return request.param


def test_dollar_sub_valid(valid_inputs_sub):
    input_value, expected = valid_inputs_sub

    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 - dollar_2).amount == Decimal(str(expected))
    assert (dollar_1 - input_value[1]).amount == Decimal(str(expected))


def test_dollar_sub_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar - invalid_case


def test_dollar_isub_valid(valid_inputs_sub):
    input_value, expected = valid_inputs_sub
    dollar: Dollar = Dollar(input_value[0])
    dollar -= Dollar(input_value[1])

    assert dollar.amount == Decimal(str(expected))

    dollar = Dollar(input_value[0])
    dollar -= input_value[1]

    assert dollar.amount == Decimal(str(expected))


def test_dollar_isub_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar -= invalid_case


def test_dollar_rsub_valid(valid_inputs_sub):
    input_value, expected = valid_inputs_sub
    dollar: Dollar = Dollar(input_value[1])

    assert (input_value[0] - dollar).amount == Decimal(str(expected))


def test_dollar_rsub_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        invalid_case - dollar


@pytest.fixture(
    params=[
        ([0, 0], 0.0),  # zero
        ([1.0, 0.005], 0.01),  # very small
        ([1e20, 10], 1e21),  # very large
        ([100, 50], 5000.0),  # int
        ([100.5, 50.25], 5050.13),  # float
        (["100.5", "50.25"], 5050.13),  # str
        ([100, -50], -5000.0),  # negative int
        ([100.5, -50.25], -5050.13),  # negative float
        (["100.5", "-50.25"], -5050.13),  # negative str
    ]
)
def valid_inputs_mul(request):
    return request.param


def test_dollar_mul_valid(valid_inputs_mul):
    input_value, expected = valid_inputs_mul
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 * dollar_2).amount == Decimal(str(expected))
    assert (dollar_1 * input_value[1]).amount == Decimal(str(expected))


def test_dollar_mul_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar * invalid_case


def test_dollar_imul_valid(valid_inputs_mul):
    input_value, expected = valid_inputs_mul
    dollar: Dollar = Dollar(input_value[0])
    dollar *= Dollar(input_value[1])

    assert dollar.amount == Decimal(str(expected))

    dollar = Dollar(input_value[0])
    dollar *= input_value[1]

    assert dollar.amount == Decimal(str(expected))


def test_dollar_imul_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar *= invalid_case


def test_dollar_rmul_valid(valid_inputs_mul):
    input_value, expected = valid_inputs_mul
    dollar: Dollar = Dollar(input_value[1])

    assert (input_value[0] * dollar).amount == Decimal(str(expected))


def test_dollar_rmul_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        invalid_case * dollar


@pytest.fixture(
    params=[
        ([0, 1], 0.0),  # zero
        ([0.005, 1], 0.01),  # very small
        ([1e20, 10], 1e19),  # very large
        ([100, 50], 2.0),  # int
        ([100.5, 60.25], 1.67),  # float
        (["100.5", "60.25"], 1.67),  # str
        ([100, -50], -2.0),  # negative int
        ([100.5, -60.25], -1.67),  # negative float
        (["100.5", "-60.25"], -1.67),  # negative str
    ]
)
def valid_inputs_truediv(request):
    return request.param


def test_dollar_truediv_valid(valid_inputs_truediv):
    input_value, expected = valid_inputs_truediv
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 / dollar_2).amount == Decimal(str(expected))
    assert (dollar_1 / input_value[1]).amount == Decimal(str(expected))


def test_dollar_truediv_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar / invalid_case


def test_dollar_itruediv_valid(valid_inputs_truediv):
    input_value, expected = valid_inputs_truediv
    dollar: Dollar = Dollar(input_value[0])
    dollar /= Dollar(input_value[1])

    assert dollar.amount == Decimal(str(expected))

    dollar = Dollar(input_value[0])
    dollar /= input_value[1]

    assert dollar.amount == Decimal(str(expected))


def test_dollar_itruediv_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar /= invalid_case


def test_dollar_rtruediv_valid(valid_inputs_truediv):
    input_value, expected = valid_inputs_truediv
    dollar: Dollar = Dollar(input_value[1])

    assert (input_value[0] / dollar).amount == Decimal(str(expected))


def test_dollar_rtruediv_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar / invalid_case


def test_dollar_divide_by_zero():
    dollar: Dollar = Dollar(100)

    with pytest.raises(ZeroDivisionError):
        dollar / 0

    dollar = Dollar(0)

    with pytest.raises(ZeroDivisionError):
        100 / dollar


# --------------------
# Comparison Operators
# --------------------
@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([0, 0], True),  # zero
        ([0.005, 0.01], True),  # very small
        ([1e20, 1e20], True),  # very large
        ([100, 100], True),  # int equal
        ([100, 50], False),  # int not equal
        ([100.5, 100.5], True),  # float equal
        ([100.5, 60.25], False),  # float not equal
        (["100.5", "100.5"], True),  # str equal
        (["100.5", "60.25"], False),  # str not equal
        ([-100, -100], True),  # negative int equal
        ([-100, -60], False),  # negative int not equal
        ([-100.5, -100.5], True),  # negative float equal
        ([-100.5, -60.25], False),  # negative float not equal
        (["-100.5", "-100.5"], True),  # negative str equal
        (["-100.5", "-60.25"], False),  # negative str not equal
    ],
)
def test_dollar_eq_valid(input_value, expected):
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 == dollar_2) == expected
    assert (dollar_1 == input_value[1]) == expected


def test_dollar_eq_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar == invalid_case


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([0, 0], False),  # zero
        ([0.005, 0.01], False),  # very small
        ([0.004, 0.01], True),  # very small
        ([0.004, 0.02], True),  # very small
        ([1e20, 2e20], True),  # very large
        ([2e20, 2e20], False),  # very large
        ([3e20, 2e20], False),  # very large
        ([100, 200], True),  # int less
        ([100, 100], False),  # int equal
        ([100, 50], False),  # int greater
        ([100.5, 200.5], True),  # float less
        ([100.5, 100.5], False),  # float equal
        ([100.5, 60.25], False),  # float greater
        (["100.5", "200.5"], True),  # str less
        (["100.5", "100.5"], False),  # str equal
        (["100.5", "60.25"], False),  # str greater
        ([-100, -10], True),  # negative int less
        ([-100, -100], False),  # negative int equal
        ([-100, -160], False),  # negative int greater
        ([-100.5, -10.5], True),  # negative float less
        ([-100.5, -100.5], False),  # negative float equal
        ([-100.5, -160.25], False),  # negative float greater
        (["-100.5", "-10.5"], True),  # negative str less
        (["-100.5", "-100.5"], False),  # negative str greater
        (["-100.5", "-160.25"], False),  # negative str greater
    ],
)
def test_dollar_lt_valid(input_value, expected):
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 < dollar_2) == expected
    assert (dollar_1 < input_value[1]) == expected


def test_dollar_lt_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar < invalid_case


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([0, 0], True),  # zero
        ([0.01, 0.004], False),  # very small
        ([0.005, 0.01], True),  # very small
        ([0.004, 0.01], True),  # very small
        ([1e20, 2e20], True),  # very large
        ([2e20, 2e20], True),  # very large
        ([3e20, 2e20], False),  # very large
        ([100, 200], True),  # int less
        ([100, 100], True),  # int equal
        ([100, 50], False),  # int greater
        ([100.5, 200.5], True),  # float less
        ([100.5, 100.5], True),  # float equal
        ([100.5, 60.25], False),  # float greater
        (["100.5", "200.5"], True),  # str less
        (["100.5", "100.5"], True),  # str equal
        (["100.5", "60.25"], False),  # str greater
        ([-100, -10], True),  # negative int less
        ([-100, -100], True),  # negative int equal
        ([-100, -160], False),  # negative int greater
        ([-100.5, -10.5], True),  # negative float less
        ([-100.5, -100.5], True),  # negative float equal
        ([-100.5, -160.25], False),  # negative float greater
        (["-100.5", "-10.5"], True),  # negative str less
        (["-100.5", "-100.5"], True),  # negative str greater
        (["-100.5", "-160.25"], False),  # negative str greater
    ],
)
def test_dollar_le_valid(input_value, expected):
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 <= dollar_2) == expected
    assert (dollar_1 <= input_value[1]) == expected


def test_dollar_le_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar <= invalid_case


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([0, 0], False),  # zero
        ([0.005, 0.02], False),  # very small
        ([0.005, 0.01], False),  # very small
        ([0.005, 0.0], True),  # very small
        ([1e20, 2e20], False),  # very large
        ([2e20, 2e20], False),  # very large
        ([3e20, 2e20], True),  # very large
        ([100, 200], False),  # int less
        ([100, 100], False),  # int equal
        ([100, 50], True),  # int greater
        ([100.5, 200.5], False),  # float less
        ([100.5, 100.5], False),  # float equal
        ([100.5, 60.25], True),  # float greater
        (["100.5", "200.5"], False),  # str less
        (["100.5", "100.5"], False),  # str equal
        (["100.5", "60.25"], True),  # str greater
        ([-100, -10], False),  # negative int less
        ([-100, -100], False),  # negative int equal
        ([-100, -160], True),  # negative int greater
        ([-100.5, -10.5], False),  # negative float less
        ([-100.5, -100.5], False),  # negative float equal
        ([-100.5, -160.25], True),  # negative float greater
        (["-100.5", "-10.5"], False),  # negative str less
        (["-100.5", "-100.5"], False),  # negative str greater
        (["-100.5", "-160.25"], True),  # negative str greater
    ],
)
def test_dollar_gt_valid(input_value, expected):
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 > dollar_2) == expected
    assert (dollar_1 > input_value[1]) == expected


def test_dollar_gt_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar > invalid_case


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([0, 0], True),  # zero
        ([0.005, 0.02], False),  # very small
        ([0.005, 0.01], True),  # very small
        ([0.005, 0.0], True),  # very small
        ([1e20, 2e20], False),  # very large
        ([2e20, 2e20], True),  # very large
        ([3e20, 2e20], True),  # very large
        ([100, 200], False),  # int less
        ([100, 100], True),  # int equal
        ([100, 50], True),  # int greater
        ([100.5, 200.5], False),  # float less
        ([100.5, 100.5], True),  # float equal
        ([100.5, 60.25], True),  # float greater
        (["100.5", "200.5"], False),  # str less
        (["100.5", "100.5"], True),  # str equal
        (["100.5", "60.25"], True),  # str greater
        ([-100, -10], False),  # negative int less
        ([-100, -100], True),  # negative int equal
        ([-100, -160], True),  # negative int greater
        ([-100.5, -10.5], False),  # negative float less
        ([-100.5, -100.5], True),  # negative float equal
        ([-100.5, -160.25], True),  # negative float greater
        (["-100.5", "-10.5"], False),  # negative str less
        (["-100.5", "-100.5"], True),  # negative str greater
        (["-100.5", "-160.25"], True),  # negative str greater
    ],
)
def test_dollar_ge_valid(input_value, expected):
    dollar_1: Dollar = Dollar(input_value[0])
    dollar_2: Dollar = Dollar(input_value[1])

    assert (dollar_1 >= dollar_2) == expected
    assert (dollar_1 >= input_value[1]) == expected


def test_dollar_ge_invalid(invalid_case):
    dollar: Dollar = Dollar(100)

    with pytest.raises(Exception):
        dollar >= invalid_case


# --------------------
# Unary Operators
# --------------------
@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, 0.0),  # zero
        (0.005, 0.01),  # very small
        (1e20, 1e20),  # very large
        (100, 100.0),  # int
        (100.5, 100.5),  # float
        ("100.5", 100.5),  # str
        (-100, 100.0),  # negative int
        (-100.5, 100.5),  # negative float
        ("-100.5", 100.5),  # negative str
    ],
)
def test_dollar_abs_valid(input_value, expected):
    dollar: Dollar = Dollar(input_value)
    result: Dollar = abs(dollar)

    assert isinstance(result, Dollar)
    assert result.amount == Decimal(str(expected))


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, 0.0),  # zero
        (0.005, -0.01),  # very small
        (1e20, -1e20),  # very large
        (100, -100.0),  # int
        (100.5, -100.5),  # float
        ("100.5", -100.5),  # str
        (-100, 100.0),  # negative int
        (-100.5, 100.5),  # negative float
        ("-100.5", 100.5),  # negative str
    ],
)
def test_dollar_neg_valid(input_value, expected):
    dollar: Dollar = Dollar(input_value)

    assert (-dollar).amount == Decimal(str(expected))


# --------------------
# Internal helpers
# --------------------
@pytest.mark.parametrize(
    "input_value, expected",
    [
        (0, 0.0),  # zero
        (0.004, 0.0),  # very small
        (0.005, 0.01),  # very small
        (1e20, 1e20),  # very large
        (100, 100.0),  # int
        (100.5, 100.5),  # float
        ("100.5", 100.5),  # str
        (-100, -100.0),  # negative int
        (-100.5, -100.5),  # negative float
        ("-100.5", -100.5),  # negative str
    ],
)
def test_to_decimal_valid_inputs(input_value, expected):
    assert Dollar._to_decimal(input_value) == Decimal(str(expected))


def test_to_decimal_invalid_inputs(invalid_case):
    with pytest.raises(TypeError):
        Dollar._to_decimal(invalid_case)


def test_from_decimal_quantization():
    d = Dollar._from_decimal(Decimal("100.456"))

    assert isinstance(d, Dollar)
    assert d.amount == Decimal("100.46")


def test_from_decimal_negative():
    d = Dollar._from_decimal(Decimal("-50.555"))

    assert d.amount == Decimal("-50.56")
