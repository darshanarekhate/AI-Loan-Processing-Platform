from database.customer_repository import (
    save_customer,
    get_customer_by_pan,
)

from utils.helpers import generate_customer_id


customer = {
    "customer_id": generate_customer_id(),
    "full_name": "Mohamed Faiz",
    "email": "faiz@example.com",
    "phone": "8610516626",
    "pan": "BZGPM5154B",
    "aadhaar": "834688652621",
    "date_of_birth": "1993-05-18",
}

save_customer(customer)

result = get_customer_by_pan("BZGPM5154B")

print(dict(result))