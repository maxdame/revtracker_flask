from flask import Blueprint, jsonify, abort, request
from ..models import db, Transaction, Contract, BillingCadence, ProductType, Invoice, invoices_transactions

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


def validate_fields(transaction_details, required_fields):
    for transaction in transaction_details:
        for field in required_fields:
            if field not in transaction:
                return False, f'{field} not provided'
    return True, None


def valid_product(product):
    valid_products = [product_type.name for product_type in ProductType]
    if product not in valid_products:
        return False, f'Product not recognized. Please select one of {valid_products}'
    return True, None


def valid_billing_cadence(billing_cadence):
    valid_cadences = [cadence.name for cadence in BillingCadence]
    if billing_cadence not in valid_cadences:
        return False, f'Billing cadence not recognized. Please select one of {valid_cadences}'
    return True, None


def valid_product_and_cadence(product, billing_cadence):
    valid_products = [product_type.name for product_type in ProductType]
    valid_cadences = [cadence.name for cadence in BillingCadence]

    if product not in valid_products:
        return False, f'product not recognized\nselect one of {valid_products}'

    if billing_cadence not in valid_cadences:
        return False, f'billing cadence not recognized\nselect one of {valid_cadences}'

    return True, None


@bp.route('', methods=['GET'])
def index():
    transactions = Transaction.query.all()
    result = [transaction.serialize() for transaction in transactions]
    if len(result) == 0:
        return jsonify('no transactions in database')
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    transaction = Transaction.query.get_or_404(id)
    return jsonify(transaction.serialize())


@bp.route('', methods=['POST'])
def create():
    contract_id = request.json['contract_id']
    transaction_details = request.json['transactions']

    required_fields = ['product', 'value',
                       'start_date', 'end_date', 'billing_cadence']

    valid, error = validate_fields(transaction_details, required_fields)
    if not valid:
        return abort(400, error)

    contract_value = Contract.query.get(contract_id).value
    total_transaction_value = sum(
        [transaction['value'] for transaction in transaction_details])

    if total_transaction_value != contract_value:
        return abort(400, f'Transaction value error.\nSubmitted transactions: {total_transaction_value}\nContract value: {contract_value}')

    results = []

    for transaction in transaction_details:
        product = transaction['product']
        value = float(transaction['value'])
        start_date = transaction['start_date']
        end_date = transaction['end_date']
        billing_cadence = transaction['billing_cadence']

        valid, error = valid_product_and_cadence(product, billing_cadence)
        if not valid:
            db.session.rollback()
            return abort(400, error)

        new_transaction = Transaction(
            contract_id=int(contract_id),
            product=product,
            value=value,
            start_date=start_date,
            end_date=end_date,
            billing_cadence=billing_cadence
        )
        db.session.add(new_transaction)
        try:
            db.session.commit()
            results.append(new_transaction.serialize())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    return jsonify(results)


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    try:
        db.session.commit()
        return jsonify(f'transaction id {transaction.id} deleted')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PATCH', 'PUT'])
def update(id: int):
    transaction = Transaction.query.get_or_404(id)
    transaction_changes = request.json['transaction_changes']

    if 'contract_id' in transaction_changes:
        transaction.contract_id = transaction_changes['contract_id']
    if 'value' in transaction_changes:
        transaction.value = float(transaction_changes['value'])
    if 'start_date' in transaction_changes:
        transaction.start_date = transaction_changes['start_date']
    if 'end_date' in transaction_changes:
        transaction.end_date = transaction_changes['end_date']
    if 'billing_cadence' in transaction_changes:
        valid, message = valid_billing_cadence(
            transaction_changes['billing_cadence'])
        if not valid:
            return abort(400, message)
        transaction.billing_cadence = transaction_changes['billing_cadence']
    if 'product' in transaction_changes:
        valid, message = valid_product(transaction_changes['product'])
        if not valid:
            return abort(400, message)
        transaction.product = transaction_changes['product']

    try:
        db.session.commit()
        return jsonify(transaction.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/invoices', methods=['GET'])
def transaction_invoices(id: int):
    transaction = Transaction.query.get_or_404(id)
    invoices = Invoice.query.join(invoices_transactions).filter_by(
        transaction_id=transaction.id).all()
    result = [invoice.serialize() for invoice in invoices]
    if len(result) == 0:
        return jsonify('transaction has no invoices')
    return jsonify(result)
