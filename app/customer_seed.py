import random
from datetime import date

from faker import Faker
from src.models import *
from src import create_app

CUSTOMERS = 30
CONTRACTS = 3
TRANSACTIONS = 2


def truncate_tables():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


def main(CUSTOMERS, CONTRACTS, TRANSACTIONS):
    app = create_app()
    app.app_context().push()
    truncate_tables()
    fake = Faker()
    product_types = [e.name for e in ProductType]
    billing_cadences = [e.name for e in BillingCadence]
    contract_statuses = [e.name for e in ContractStatus]
    payment_terms = [e.name for e in PaymentTerms]

    start_date = date(2021, 1, 1)
    end_date = date(2023, 12, 31)

    with app.app_context():
        for _ in range(CUSTOMERS):
            customer = Customer(
                name=fake.name(),
                address_line_1=fake.street_address(),
                address_line_2=fake.secondary_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.zipcode(),
                country=fake.country(),
            )
            db.session.add(customer)
            db.session.commit()

            for _ in range(CONTRACTS):
                contract_start_date = fake.date_between(
                    start_date=start_date, end_date=end_date)
                contract_end_date = fake.date_between(
                    start_date=contract_start_date, end_date=end_date)
                contract_value = fake.pydecimal(
                    left_digits=5, right_digits=2, positive=True)
                contract = Contract(
                    start_date=contract_start_date,
                    end_date=contract_end_date,
                    value=contract_value,
                    status=random.choice(contract_statuses),
                    customer_id=customer.id,
                )
                db.session.add(contract)
                db.session.commit()

                value_per_transaction = contract_value / TRANSACTIONS

                for i in range(TRANSACTIONS):
                    transaction_start_date = fake.date_between(
                        start_date=contract_start_date, end_date=contract_end_date)
                    transaction_end_date = fake.date_between(
                        start_date=transaction_start_date, end_date=contract_end_date)
                    # Adjust last transaction value if total doesn't match contract value
                    if i == TRANSACTIONS - 1:
                        transaction_value = contract_value - \
                            value_per_transaction * (TRANSACTIONS - 1)
                    else:
                        transaction_value = value_per_transaction
                    transaction = Transaction(
                        product=random.choice(product_types),
                        value=transaction_value,
                        start_date=transaction_start_date,
                        end_date=transaction_end_date,
                        billing_cadence=random.choice(billing_cadences),
                        contract_id=contract.id,
                    )
                    db.session.add(transaction)
                    db.session.commit()


main(CUSTOMERS, CONTRACTS, TRANSACTIONS)
