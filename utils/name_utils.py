from difflib import SequenceMatcher


def normalize_name(name: str | None) -> str:
    if not name:
        return ""

    return " ".join(name.upper().split())


def name_similarity(name1: str | None, name2: str | None) -> float:
    """
    Similarity of two names in percent (0-100).

    Token order is ignored, so "KUMAR RAVI" and "RAVI KUMAR" match.
    """

    a = normalize_name(name1)
    b = normalize_name(name2)

    if not a or not b:
        return 0.0

    direct = SequenceMatcher(None, a, b).ratio()
    sorted_tokens = SequenceMatcher(
        None,
        " ".join(sorted(a.split())),
        " ".join(sorted(b.split())),
    ).ratio()

    return round(max(direct, sorted_tokens) * 100, 2)
