from pathlib import Path
import shutil


UPLOAD_FOLDER = Path("uploads")


def save_uploaded_file(
    uploaded_file,
    customer_id,
    application_id,
):

    folder = (
        UPLOAD_FOLDER
        / customer_id
        / application_id
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = folder / uploaded_file.name

    with open(destination, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    return str(destination)