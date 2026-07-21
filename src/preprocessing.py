import cv2


def preprocess_image(path):

    image = cv2.imread(path)

    if image is None:
        raise Exception("Image Not Found")

    image = cv2.resize(
        image,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.bilateralFilter(
        gray,
        11,
        17,
        17
    )

    return gray