import cv2
import sqlite3
import re
import pytesseract

from pytesseract import Output

from config import DATABASE_PATH
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def perform_ocr(image):

    config="--oem 3 --psm 6"

    text=pytesseract.image_to_string(

        image,

        config=config

    )

    data=pytesseract.image_to_data(

        image,

        output_type=Output.DICT,

        config=config

    )

    conf=[]

    for c in data["conf"]:

        try:

            c=float(c)

            if c>0:

                conf.append(c)

        except:

            pass

    avg=round(sum(conf)/len(conf),2) if conf else 0

    return text,avg

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

    dob_pattern = r"\d{2}/\d{2}/\d{4}"

    for line in lines:

        match = re.search(dob_pattern, line)

        if match:
            dob = match.group()
            break

    # ------------------------------------
    # Extract Name
    # (Next line after PAN Number)
    # ------------------------------------

    if pan_number:

        for i, line in enumerate(lines):

            if pan_number in line.upper():

                if i + 1 < len(lines):

                    candidate = lines[i + 1]

                    # Remove symbols
                    candidate = re.sub(r'[^A-Za-z ]', ' ', candidate)

                    candidate = re.sub(r'\s+', ' ', candidate).strip()

                    # Keep only fully uppercase words
                    words = [w for w in candidate.split() if w.isupper()]

                    # Stop if OCR starts adding lowercase/noise
                    clean_words = []
                    for w in words:
                        if len(w) >= 2:
                            clean_words.append(w)
                        else:
                            break

                    if len(clean_words) >= 2:
                        name = " ".join(clean_words[:2])

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

    return {

        "PAN": pan_number,
        "NAME": name,
        "FATHER": father_name,
        "DOB": dob

    }

def save_ocr_result(
    document_id,
    number,
    confidence,
    name,
    father,
    dob
):

    conn = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET
            extracted_number=?,
            ocr_confidence=?,
            name=?,
            father_name=?,
            dob=?
        WHERE id=?
        """,
        (
            number,
            confidence,
            name,
            father,
            dob,
            document_id
        )
    )

    conn.commit()
    conn.close()


def extract_aadhaar_details(ocr_text):

    import re

    lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]

    aadhaar = None
    name = None
    dob = None

    # -----------------------------------
    # Aadhaar Number
    # -----------------------------------

    aadhaar_pattern = r"\d{4}\s?\d{4}\s?\d{4}"

    for line in lines:

        match = re.search(aadhaar_pattern, line)

        if match:

            aadhaar = match.group().replace(" ", "")

            break

    # -----------------------------------
    # DOB
    # -----------------------------------

    dob_pattern = r"\d{2}/\d{2}/\d{4}"

    for line in lines:

        match = re.search(dob_pattern, line)

        if match:

            dob = match.group()

            break

    # -----------------------------------
    # Name
    # -----------------------------------

    for line in lines:

        line = re.sub(r"[^A-Za-z ]", "", line).strip()

        words = line.split()

        if len(words) >= 2:

            if all(word.isupper() for word in words):

                if "GOVERNMENT" not in line and "INDIA" not in line:

                    name = line

                    break

    return {
        "AADHAAR": aadhaar,
        "NAME": name,
        "DOB": dob
    }