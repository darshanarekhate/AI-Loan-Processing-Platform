from uuid import uuid4

def generate_customer_id():
    return f"CUST-{uuid4().hex[:8].upper()}"

def generate_application_id():
    return f"APP-{uuid4().hex[:8].upper()}"