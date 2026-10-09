import logging
import re

import pytesseract

from pytesseract import Output

from config import TESSERACT_PATH
from src.easyocr_reader import perform_easyocr

logger = logging.getLogger(__name__)

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def perform_ocr(image, document_type="PAN"):

    if document_type == "AADHAAR":
        configs = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 4"
        ]
    else:
        configs = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 11"
        ]

    best_text = ""
    best_conf = 0.0

    for config in configs:


        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config=config,
            timeout=20
        )


        data = pytesseract.image_to_data(
            image,
            lang="eng",
            output_type=Output.DICT,
            config=config
        )

        confidences = []

        for c in data["conf"]:
            try:
                c = float(c)
                if c > 0:
                    confidences.append(c)
            except ValueError:
                pass

        avg_conf = round(
            sum(confidences) / len(confidences),
            2
        ) if confidences else 0.0

        logger.debug("Tesseract %s -> confidence %s", config, avg_conf)

        # Exit early if confidence is excellent
        if avg_conf >= 70:
            logger.debug("High confidence achieved; skipping remaining configs")
            best_text = text
            best_conf = avg_conf
            break

        # Keep best result
        if avg_conf > best_conf:
            best_conf = avg_conf
            best_text = text

    logger.debug("Best Tesseract confidence: %s", best_conf)

    # EasyOCR fallback threshold
    threshold = 50 if document_type == "AADHAAR" else 60

    if best_conf < threshold:

        logger.debug("Low confidence; trying EasyOCR")

        easy_text, easy_conf = perform_easyocr(image)

        logger.debug("EasyOCR confidence: %s", easy_conf)

        if easy_conf > best_conf:
            return easy_text, easy_conf

    return best_text, best_conf

def extract_pan_details(ocr_text):

    lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]

    pan_number = None
    name = None
    father_name = None
    dob = None

    # ------------------------------------
    # Extract PAN Number
    # ------------------------------------

    pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]"

    for line in lines:

        match = re.search(pan_pattern, line.upper())

        if match:
            pan_number = match.group()
            break

    # ------------------------------------
    # Extract DOB
    # ------------------------------------

    dob = None

    dob_patterns = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{2}\.\d{2}\.\d{4}"
    ]

    for line in lines:
        for pattern in dob_patterns:
            match = re.search(pattern, line)
            if match:
                dob = match.group()
                break

        if dob:
            break

    # ------------------------------------
    # Extract Father's Name
    # ------------------------------------
    
    for i, line in enumerate(lines):
    
        if "FATHER" in line.upper():
    
            if i + 1 < len(lines):
    
                candidate = lines[i + 1]
    
                candidate = re.sub(r'[^A-Za-z ]', ' ', candidate)
    
                candidate = re.sub(r'\s+', ' ', candidate).strip()
    
                words = [w for w in candidate.split() if w.isupper()]
    
                if len(words) >= 2:
                        father_name = " ".join(words)
    
            break

    # ------------------------------------
    # Extract Applicant Name
    # ------------------------------------

    name = None

    if pan_number:

        for i, line in enumerate(lines):

            if pan_number in line.upper():

                # Look at the next 5 lines after PAN number
                for j in range(i + 1, min(i + 6, len(lines))):

                    candidate = re.sub(r"[^A-Za-z ]", "", lines[j]).strip().upper()

                    words = candidate.split()

                    if len(words) < 2:
                        continue

                    ignore = [
                        "INCOME",
                        "TAX",
                        "DEPARTMENT",
                        "GOVT",
                        "GOVERNMENT",
                        "INDIA",
                        "PERMANENT",
                        "ACCOUNT",
                        "NUMBER",
                        "CARD",
                        "NAME",
                        "FATHER",
                        "DATE",
                        "BIRTH",
                        "SIGNATURE"
                    ]

                    if any(word in ignore for word in words):
                        continue

                    # First valid uppercase line is applicant name
                    if all(word.isalpha() for word in words):

                        clean_words = []

                        for word in words:

                            # Stop when OCR starts producing noisy words
                            if len(word) < 2:
                                break

                            if word in [
                                "DC",
                                "OS",
                                "SEERS",
                                "SIGNATURE",
                                "DATE",
                                "BIRTH",
                                "FATHER",
                                "NAME"
                            ]:
                                break

                            clean_words.append(word)

                        if len(clean_words) >= 2:
                            name = " ".join(clean_words)
                            break

                break

    return {

        "PAN": pan_number,
        "NAME": name,
        "FATHER": father_name,
        "DOB": dob

    }

def extract_aadhaar_details(ocr_text):

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in ocr_text.split("\n")
        if line.strip()
    ]

    aadhaar = None
    dob = None
    name = None

    # ------------------------------------
    # Aadhaar Number
    # ------------------------------------

    aadhaar_pattern = r"(?:\d{4}\s?){2}\d{4}"

    for line in lines:

        match = re.search(aadhaar_pattern, line)

        if match:

            aadhaar = match.group().replace(" ", "")
            break

    # ------------------------------------
    # DOB
    # ------------------------------------

    dob_patterns = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{2}\.\d{2}\.\d{4}"
    ]

    dob_index = -1

    for i, line in enumerate(lines):

        for pattern in dob_patterns:

            match = re.search(pattern, line)

            if match:

                dob = match.group()
                dob_index = i
                break

        if dob:
            break

    # ------------------------------------
    # Find Name Near DOB
    # ------------------------------------

    ignore_words = {

        "GOVERNMENT",
        "INDIA",
        "UIDAI",
        "UNIQUE",
        "IDENTIFICATION",
        "AUTHORITY",
        "AADHAAR",
        "ADDRESS",
        "MALE",
        "FEMALE",
        "DOB",
        "YEAR",
        "BIRTH",
        "PROOF",
        "IDENTITY",
        "CITIZENSHIP",
        "ONLINE",
        "AUTHENTICATION",
        "QR",
        "CODE",
        "XML"

    }

    candidates = []

    if dob_index != -1:

        start = max(0, dob_index - 3)

        for i in range(start, dob_index):

            candidate = lines[i]

            candidate = re.sub(
                r"[^A-Za-z ]",
                " ",
                candidate
            )

            candidate = re.sub(
                r"\s+",
                " ",
                candidate
            ).strip()

            if len(candidate) < 4:
                continue

            upper = candidate.upper()

            if any(word in upper for word in ignore_words):
                continue

            words = candidate.split()

            # Aadhaar names normally contain 2-3 words
            if len(words) < 2 or len(words) > 4:
                continue

            clean_words = []

            for word in words:

                if len(word) < 2:
                    continue

                # Ignore OCR garbage
                if not word.isalpha():
                    continue

                clean_words.append(word)

            if len(clean_words) >= 2:

                # Remove suspicious trailing OCR fragment
                if (
                    len(clean_words) >= 3
                    and len(clean_words[-1]) <= 2
                ):
                    clean_words = clean_words[:-1]

                candidate = " ".join(clean_words)

                score = 0

                score += 10 - (dob_index - i)

                if 2 <= len(clean_words) <= 3:
                    score += 5

                if all(2 <= len(w) <= 12 for w in clean_words):
                    score += 3

                candidates.append(
                    (
                        score,
                        candidate
                    )
                )

    if candidates:

        candidates.sort(
            reverse=True
        )

        name = candidates[0][1].title()

    return {

        "AADHAAR": aadhaar,

        "NAME": name,

        "DOB": dob

    }
