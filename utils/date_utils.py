from datetime import datetime


def normalize_date(date_string):
    """
    Converts different date formats into YYYY-MM-DD.
    """

    if not date_string:
        return None

    date_string = date_string.strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                date_string,
                fmt
            ).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return date_string