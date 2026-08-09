from database.loan_repository import get_loans_by_customer

customer_id = "CUST-979F04AB"   # Replace with your customer ID if different

loans = get_loans_by_customer(customer_id)

if loans:
    for loan in loans:
        print(dict(loan))
else:
    print("No loan applications found.")