import io

import pytest

from mcp_server.policy_facts import (
    parse_eligible_vehicles,
    parse_ltv_percent,
    parse_tenure_months,
    read_policy,
)
from utils.date_utils import normalize_date
from utils.file_handler import UploadError, save_uploaded_file, validate_upload
from utils.masking import mask_aadhaar, mask_pan, mask_phone
from utils.name_utils import name_similarity


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


# ------------------------------------------------------------
# Masking
# ------------------------------------------------------------

def test_masking_hides_identifiers():
    assert mask_pan("ABCPE1234F") == "ABCPE****F"
    assert mask_aadhaar("234567890124") == "********0124"
    assert mask_phone("9876543210") == "******3210"


@pytest.mark.parametrize("value", [None, "", "12"])
def test_masking_handles_short_or_missing(value):
    assert "*" in mask_pan(value)
    assert "*" in mask_aadhaar(value)
    assert "*" in mask_phone(value)


# ------------------------------------------------------------
# Names and dates
# ------------------------------------------------------------

def test_name_similarity_ignores_case_spacing_and_order():
    assert name_similarity("ravi  kumar", "RAVI KUMAR") == 100
    assert name_similarity("Kumar Ravi", "Ravi Kumar") == 100
    assert name_similarity("Ravi Kumar", "Suresh Iyer") < 60
    assert name_similarity(None, "Ravi") == 0


@pytest.mark.parametrize("raw", ["15/07/1990", "15-07-1990", "15.07.1990", "1990-07-15"])
def test_normalize_date(raw):
    assert normalize_date(raw) == "1990-07-15"


# ------------------------------------------------------------
# Uploads
# ------------------------------------------------------------

class FakeUpload(io.BytesIO):
    def __init__(self, name, content):
        super().__init__(content)
        self.name = name


def test_upload_rejects_wrong_extension():
    with pytest.raises(UploadError):
        validate_upload("payload.exe", b"MZ")


def test_upload_rejects_spoofed_content():
    with pytest.raises(UploadError):
        validate_upload("pan.png", b"%PDF-1.7 not an image")


def test_upload_ignores_client_path_traversal():
    path = save_uploaded_file(
        FakeUpload("../../app.py.png", PNG),
        "CUST-ABCD1234",
        "APP-ABCD1234",
        "PAN",
    )

    assert path.endswith("PAN.png")
    assert ".." not in path


def test_upload_rejects_unsafe_ids():
    with pytest.raises(UploadError):
        save_uploaded_file(FakeUpload("pan.png", PNG), "../etc", "APP-1", "PAN")


# ------------------------------------------------------------
# Policy facts used by the MCP server
# ------------------------------------------------------------

def test_policy_facts_parse_car_loan_document():
    text = read_policy("car_loan.txt")

    assert parse_ltv_percent(text) == 90
    assert parse_tenure_months(text) == (12, 84)
    assert "SUVs" in parse_eligible_vehicles(text)
    assert len(parse_eligible_vehicles(text)) == 6
