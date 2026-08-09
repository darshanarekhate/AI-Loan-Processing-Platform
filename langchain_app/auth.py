import bcrypt

from database.user_repository import (
    get_user_by_username,
    update_last_login,
)


def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def authenticate_user(
    username: str,
    password: str,
):

    user = get_user_by_username(username)

    if not user:
        return None

    if not user["is_active"]:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    update_last_login(user["user_id"])

    return dict(user)