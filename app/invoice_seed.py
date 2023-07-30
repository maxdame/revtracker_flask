from dateutil.relativedelta import relativedelta
from collections import defaultdict
from dateutil.parser import parse
from src.models import *
from src import create_app


def generate_invoice_dates(start_date, billing_cadence, num_of_invoices):
    invoice_dates = []
    for _ in range(int(num_of_invoices)):
        invoice_dates.append(start_date)
        if billing_cadence == "monthly":
            start_date += relativedelta(months=+1)
        elif billing_cadence == "quarterly":
            start_date += relativedelta(months=+3)
        elif billing_cadence == "annually":
            start_date += relativedelta(years=+1)
    return invoice_dates


def calculate_num_of_invoices(months, billing_cadence):
    if billing_cadence == "monthly":
        return max(int(months), 1)
    if billing_cadence == "quarterly":
        return max(int(months // 3), 1)
    if billing_cadence == "annually":
        return max(int(months // 12), 1)


def main():
    app = create_app()
    app.app_context().push()
    contracts = Contract.query.all()
    with app.app_context():
        for contract in contracts:
            contract_id = contract.id
            contract_details = Contract.query.get_or_404(contract_id)

            # is_invoiced = Invoice.query.filter_by(contract_id=contract_id).first()
            # if is_invoiced:
            #     return abort(400, "invoices have already been created for this contract")

            transactions = Transaction.query.filter_by(
                contract_id=contract_id).all()

            invoice_groups = defaultdict(list)

            for transaction in transactions:
                billing_cadence = transaction.billing_cadence.name
                value = transaction.value
                transaction_start_date = parse(
                    transaction.start_date.strftime('%Y-%m-%d'))
                transaction_end_date = parse(
                    transaction.end_date.strftime('%Y-%m-%d'))

                difference = relativedelta(
                    transaction_end_date, transaction_start_date)
                months = difference.years * 12 + difference.months + 1

                num_of_invoices = calculate_num_of_invoices(
                    months, billing_cadence)
                invoice_dates = generate_invoice_dates(
                    transaction_start_date, billing_cadence, num_of_invoices)
                per_invoice_amount = round(value / num_of_invoices, 2)

                for date in invoice_dates:
                    invoice_groups[date.strftime(
                        '%Y-%m-%d')].append((transaction, per_invoice_amount))

            for date, transactions_and_amounts in invoice_groups.items():
                total_amount_due = sum(
                    amount for _, amount in transactions_and_amounts)
                new_invoice = Invoice(parse(date), PaymentTerms.due_upon_receipt.name,
                                      contract_details.customer_id, contract_id, total_amount_due)
                new_invoice.transactions = (
                    [transaction for transaction, _ in transactions_and_amounts])
                db.session.add(new_invoice)
                db.session.commit()


main()
