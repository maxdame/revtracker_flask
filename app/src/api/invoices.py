from flask import Blueprint, jsonify, abort, request
from ..models import db, Invoice, Transaction, Contract, PaymentTerms, invoices_transactions
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from collections import defaultdict


bp = Blueprint('invoices', __name__, url_prefix='/invoices')


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
        return int(months)
    if billing_cadence == "quarterly":
        return int(months // 3)
    if billing_cadence == "annually":
        return int(months // 12)


@bp.route('', methods=['GET'])
def index():
    invoices = Invoice.query.all()
    result = [invoice.serialize() for invoice in invoices]
    if len(result) == 0:
        return jsonify('no invoices in database')
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    invoice = Invoice.query.get_or_404(id)
    return jsonify(invoice.serialize())


@bp.route('', methods=['POST'])
def create():
    contract_id = request.json['contract_id']
    contract_details = Contract.query.get_or_404(contract_id)

    is_invoiced = Invoice.query.filter_by(contract_id=contract_id).first()
    if is_invoiced:
        return abort(400, "invoices have already been created for this contract")

    transactions = Transaction.query.filter_by(contract_id=contract_id).all()

    invoice_groups = defaultdict(list)

    for transaction in transactions:
        billing_cadence = transaction.billing_cadence.name
        value = transaction.value
        transaction_start_date = parse(
            transaction.start_date.strftime('%Y-%m-%d'))
        transaction_end_date = parse(transaction.end_date.strftime('%Y-%m-%d'))

        difference = relativedelta(
            transaction_end_date, transaction_start_date)
        months = difference.years * 12 + difference.months + 1

        num_of_invoices = calculate_num_of_invoices(months, billing_cadence)
        invoice_dates = generate_invoice_dates(
            transaction_start_date, billing_cadence, num_of_invoices)
        per_invoice_amount = round(value / num_of_invoices, 2)

        for date in invoice_dates:
            invoice_groups[date.strftime(
                '%Y-%m-%d')].append((transaction, per_invoice_amount))

    results = []

    for date, transactions_and_amounts in invoice_groups.items():
        total_amount_due = sum(
            amount for _, amount in transactions_and_amounts)
        new_invoice = Invoice(parse(date), PaymentTerms.due_upon_receipt.name,
                              contract_details.customer_id, contract_id, total_amount_due)
        new_invoice.transactions = (
            [transaction for transaction, _ in transactions_and_amounts])
        db.session.add(new_invoice)
        db.session.commit()
        results.append(new_invoice.serialize())

    return jsonify(results)


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    try:
        db.session.commit()
        return jsonify(f'invoice id {invoice.id} deleted')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['PATCH', 'PUT'])
def update():
    contract_id = request.json['contract_id']
    contract_details = Contract.query.get_or_404(contract_id)
    transactions = Transaction.query.filter_by(contract_id=contract_id).all()

    # Generate expected invoice details based on current transaction details
    expected_invoice_groups = defaultdict(list)
    for transaction in transactions:
        billing_cadence = transaction.billing_cadence.name
        value = transaction.value
        transaction_start_date = parse(
            transaction.start_date.strftime('%Y-%m-%d'))
        transaction_end_date = parse(transaction.end_date.strftime('%Y-%m-%d'))

        difference = relativedelta(
            transaction_end_date, transaction_start_date)
        months = difference.years * 12 + difference.months + 1

        num_of_invoices = calculate_num_of_invoices(months, billing_cadence)
        invoice_dates = generate_invoice_dates(
            transaction_start_date, billing_cadence, num_of_invoices)
        per_invoice_amount = round(value / num_of_invoices, 2)

        for date in invoice_dates:
            expected_invoice_groups[date.strftime(
                '%Y-%m-%d')].append((transaction, per_invoice_amount))
    # Get existing invoices
    existing_invoices = Invoice.query.filter_by(contract_id=contract_id).all()
    existing_invoice_dates = [invoice.date.strftime(
        '%Y-%m-%d') for invoice in existing_invoices]
    # Delete existing invoices that are not in the expected_invoice_groups
    for invoice in existing_invoices:
        invoice_date = invoice.date.strftime('%Y-%m-%d')
        if invoice_date not in expected_invoice_groups:
            db.session.delete(invoice)
            existing_invoice_dates.remove(invoice_date)
    # Update existing invoices
    for invoice in existing_invoices:
        invoice_date = invoice.date.strftime('%Y-%m-%d')
        if invoice_date in expected_invoice_groups:
            expected_transactions_and_amounts = expected_invoice_groups[invoice_date]
            amount_due = sum(
                amount for _, amount in expected_transactions_and_amounts)
            invoice.amount_due = amount_due
            invoice.transactions = [
                transaction for transaction, _ in expected_transactions_and_amounts]

    # Create new invoices for any expected invoice dates that do not have an existing invoice
    for invoice_date, transactions_and_amounts in expected_invoice_groups.items():
        if invoice_date not in existing_invoice_dates:
            total_amount_due = sum(
                amount for _, amount in transactions_and_amounts)
            new_invoice = Invoice(parse(invoice_date), PaymentTerms.due_upon_receipt.name,
                                  contract_details.customer_id, contract_id, total_amount_due)
            new_invoice.transactions = [
                transaction for transaction, _ in transactions_and_amounts]
            db.session.add(new_invoice)

    try:
        db.session.commit()
        return jsonify([invoice.serialize() for invoice in Invoice.query.filter_by(contract_id=contract_id).all()])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/transactions', methods=['GET'])
def invoice_transactions(id: int):
    invoice = Invoice.query.get_or_404(id)
    transactions = Transaction.query.join(invoices_transactions).filter_by(
        invoice_id=invoice.id).all()
    result = [transaction.serialize() for transaction in transactions]
    if len(result) == 0:
        return abort(400, 'invoice has no transactions')
    return jsonify(result)
