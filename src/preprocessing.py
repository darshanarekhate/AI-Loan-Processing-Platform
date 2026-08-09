import cv2
import numpy as np


def preprocess_image(path, document_type):
    """
    Preprocess PAN / Aadhaar images before OCR.

    Steps:
    1. Read image
    2. Resize (if large)
    3. Convert to Grayscale
    4. Noise Removal
    5. Contrast Enhancement
    6. Adaptive Threshold
    7. Morphological Cleanup
    8. Sharpen Image

    Returns:
        Processed grayscale image
    """

    image = cv2.imread(path)

    if image is None:
        raise Exception(f"Image not found: {path}")

    # ------------------------------------
    # Resize Large Images
    # ------------------------------------

    height, width = image.shape[:2]

    max_width = 1800

    scale = 1.0

    if width > max_width:
        scale = max_width / width

    image = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA
    )

    # ------------------------------------
    # Convert to Grayscale
    # ------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # ------------------------------------
    # Document Specific Processing
    # ------------------------------------

    if document_type == "PAN":

        # Preserve edges while removing noise
        gray = cv2.bilateralFilter(
            gray,
            9,
            75,
            75
        )

    else:

        # Strong denoising for Aadhaar
        gray = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21
        )

        # Improve local contrast
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        gray = clahe.apply(gray)

    # ------------------------------------
    # Adaptive Threshold
    # ------------------------------------

    gray = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    # ------------------------------------
    # Morphological Cleanup
    # ------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2)
    )

    gray = cv2.morphologyEx(
        gray,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ------------------------------------
    # Sharpen Image
    # ------------------------------------

    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    gray = cv2.filter2D(
        gray,
        -1,
        sharpen_kernel
    )

    return gray