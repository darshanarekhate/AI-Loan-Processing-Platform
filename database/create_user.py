from langchain_app.auth import hash_password
from database.user_repository import create_user


password = "Loan@123"

password_hash = hash_password(password)

create_user(
    username="faiz",
    email="faiz@example.com",
    password_hash=password_hash,
    role="customer",
    customer_id="CUST-B0BC50BB",
)

print("Customer user created successfully.")