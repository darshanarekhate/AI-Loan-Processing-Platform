"""
Create a login for the AI Loan Processing System.

Examples:

    python -m scripts.create_user --role admin --username admin --email admin@example.com
    python -m scripts.create_user --role customer --username ravi \
        --email ravi@example.com --customer-id CUST-1A2B3C4D

The password is prompted for (never passed on the command line).
"""

import argparse
import getpass
import sqlite3
import sys

from database.customer_repository import get_customer_by_id
from database.schema import init_db
from database.user_repository import create_user
from langchain_app.auth import hash_password
from utils.validators import is_valid_email


MIN_PASSWORD_LENGTH = 8


def password_problem(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

    if password.isalpha() or password.isdigit():
        return "Password must mix letters with digits or symbols."

    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--role",
        choices=["admin", "officer", "customer"],
        default="customer",
    )
    parser.add_argument(
        "--customer-id",
        help="Required for customer logins (e.g. CUST-1A2B3C4D).",
    )
    args = parser.parse_args(argv)

    init_db()

    if not is_valid_email(args.email):
        parser.error("Invalid email address.")

    if args.role == "customer":
        if not args.customer_id:
            parser.error("--customer-id is required for customer users.")

        if not get_customer_by_id(args.customer_id):
            parser.error(f"Customer {args.customer_id} does not exist.")

    password = getpass.getpass("Password: ")
    problem = password_problem(password)

    if problem:
        print(problem, file=sys.stderr)
        return 1

    if getpass.getpass("Confirm password: ") != password:
        print("Passwords do not match.", file=sys.stderr)
        return 1

    try:
        create_user(
            username=args.username,
            email=args.email,
            password_hash=hash_password(password),
            role=args.role,
            customer_id=args.customer_id if args.role == "customer" else None,
        )
    except sqlite3.IntegrityError:
        print("Username or email already exists.", file=sys.stderr)
        return 1

    print(f"User '{args.username}' ({args.role}) created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
