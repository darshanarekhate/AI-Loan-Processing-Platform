from datetime import date

import pytest

from tests.conftest import OTHER_AADHAAR, VALID_AADHAAR, VALID_PAN
from utils.validators import (
    calculate_age,
    is_valid_aadhaar,
    is_valid_email,
    is_valid_pan,
    is_valid_phone,
    validate_registration_fields,
    verhoeff_is_valid,
)


@pytest.mark.parametrize("pan", [VALID_PAN, "abcpe1234f", " ABCCX9999Z "])
def test_valid_pan(pan):
    assert is_valid_pan(pan)


@pytest.mark.parametrize(
    "pan",
    ["", None, "ABCDE1234", "ABCPE12345", "1BCPE1234F", "ABCZE1234F"],
)
def test_invalid_pan(pan):
    assert not is_valid_pan(pan)


def test_verhoeff_accepts_valid_and_rejects_single_digit_typo():
    assert verhoeff_is_valid(VALID_AADHAAR)
    assert verhoeff_is_valid(OTHER_AADHAAR)

    typo = VALID_AADHAAR[:-1] + "3"
    assert not verhoeff_is_valid(typo)


def test_verhoeff_rejects_adjacent_transposition():
    swapped = VALID_AADHAAR[1] + VALID_AADHAAR[0] + VALID_AADHAAR[2:]
    assert not verhoeff_is_valid(swapped)


@pytest.mark.parametrize("aadhaar", [VALID_AADHAAR, "2345 6789 0124", "2345-6789-0124"])
def test_valid_aadhaar_formats(aadhaar):
    assert is_valid_aadhaar(aadhaar)


@pytest.mark.parametrize(
    "aadhaar",
    ["", "123456789012", "034567890124", "23456789012", "234567890123", "abcd56789012"],
)
def test_invalid_aadhaar(aadhaar):
    assert not is_valid_aadhaar(aadhaar)


@pytest.mark.parametrize("phone", ["9876543210", "+919876543210", "09876543210"])
def test_valid_phone(phone):
    assert is_valid_phone(phone)


@pytest.mark.parametrize("phone", ["12345", "5876543210", "98765432101"])
def test_invalid_phone(phone):
    assert not is_valid_phone(phone)


def test_email():
    assert is_valid_email("a.b@example.co.in")
    assert not is_valid_email("not-an-email")


def test_age_calculation_handles_birthday_not_reached():
    assert calculate_age(date(2000, 12, 31), today=date(2026, 6, 1)) == 25
    assert calculate_age(date(2000, 1, 1), today=date(2026, 6, 1)) == 26


def test_registration_happy_path():
    ok, message = validate_registration_fields(
        "Ravi Kumar", "9876543210", VALID_PAN, VALID_AADHAAR,
        email="ravi@example.com", date_of_birth=date(1990, 1, 1),
    )
    assert ok, message


def test_registration_rejects_minor():
    ok, message = validate_registration_fields(
        "Ravi Kumar", "9876543210", VALID_PAN, VALID_AADHAAR,
        date_of_birth=date.today().replace(year=date.today().year - 10),
    )
    assert not ok
    assert "18" in message


def test_registration_rejects_bad_aadhaar_checksum():
    ok, message = validate_registration_fields(
        "Ravi Kumar", "9876543210", VALID_PAN, "234567890123",
    )
    assert not ok
    assert "Aadhaar" in message
