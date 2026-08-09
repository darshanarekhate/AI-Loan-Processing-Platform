import easyocr

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


def perform_easyocr(image):

    results = reader.readtext(image)

    text = ""

    confidence_scores = []

    for result in results:

        _, detected_text, confidence = result

        text += detected_text + "\n"

        confidence_scores.append(confidence * 100)

    if confidence_scores:
        avg_confidence = round(
            sum(confidence_scores) / len(confidence_scores),
            2
        )
    else:
        avg_confidence = 0

    return text, avg_confidence