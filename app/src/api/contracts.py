from flask import Blueprint, jsonify, abort, request
from ..models import db, Contract, Customer, ContractStatus, Transaction, Invoice

bp = Blueprint('contracts', __name__, url_prefix='/contracts')


@bp.route('', methods=['GET'])
def index():
    contracts = Contract.query.all()
    result = [contract.serialize() for contract in contracts]
    if len(result) == 0:
        return jsonify('no contracts in database')
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    contract = Contract.query.get_or_404(id)
    return jsonify(contract.serialize())


@bp.route('', methods=['POST'])
def create():
    new_contract = request.json
    required_fields = ['name', 'start_date', 'end_date', 'value']
    for field in required_fields:
        if field not in new_contract:
            return abort(400, f'{field} not provided')
    customer = Customer.query.filter_by(name=new_contract['name']).first()
    contract = Contract(
        customer_id=customer.id,
        start_date=new_contract['start_date'],
        end_date=new_contract['end_date'],
        value=float(new_contract['value']),
        status=ContractStatus.draft.value
    )
    db.session.add(contract)
    try:
        db.session.commit()
        return jsonify(contract.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    contract = Contract.query.get_or_404(id)
    db.session.delete(contract)
    try:
        db.session.commit()
        return jsonify(f'contract id {contract.id} deleted')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PATCH', 'PUT'])
def update(id: int):
    contract = Contract.query.get_or_404(id)
    if 'contract_changes' not in request.json:
        return abort(400, 'contract changes not provided')
    contract_changes = request.json['contract_changes']
    if 'name' in contract_changes:
        name = contract_changes['name']
        new_customer = Customer.query.filter_by(name=name).first()
        if new_customer is None:
            abort(404, 'new customer not found')
        contract.customer_id = new_customer.id
    if 'start_date' in contract_changes:
        contract.start_date = contract_changes['start_date']
    if 'end_date' in contract_changes:
        contract.end_date = contract_changes['end_date']
    if 'status' in contract_changes:
        contract.status = contract_changes['status']
    if 'value' in contract_changes:
        contract.value = contract_changes['value']
    try:
        db.session.commit()
        return jsonify(contract.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/transactions', methods=['GET'])
def contract_transactions(id: int):
    contract = Contract.query.get_or_404(id)
    transactions = Transaction.query.filter_by(contract_id=contract.id)
    result = [transaction.serialize() for transaction in transactions]
    if len(result) == 0:
        return jsonify('contract has no transactions')
    return jsonify(result)

@bp.route('/<int:id>/invoices', methods=['GET'])
def contract_invoices(id: int):
    contract = Contract.query.get_or_404(id)
    invoices = Invoice.query.filter_by(contract_id=contract.id)
    result = [invoice.serialize() for invoice in invoices]
    if len(result) == 0:
        return jsonify('contract has no invoices')
    return jsonify(result)