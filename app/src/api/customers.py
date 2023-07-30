from flask import Blueprint, jsonify, abort, request
from ..models import db, Customer, Contract, Invoice

bp = Blueprint('customers', __name__, url_prefix='/customers')


def parse_address_create():
    address = request.json['address']
    address_line_1 = address['address_line_1']
    if not address_line_1:
        abort(400, 'address_line_1 is required')
    address_line_2 = address['address_line_2']
    city = address['city']
    if not city:
        abort(400, 'city is required')
    state = address['state']
    if not state:
        abort(400, 'state is required')
    zip_code = address['zip_code']
    if not zip_code:
        abort(400, 'zip_code is required')
    country = address['country']
    if not country:
        abort(400, 'country is required')
    return address_line_1, address_line_2, city, state, zip_code, country


def parse_address_update():
    address = request.json['address']
    address_line_1 = address['address_line_1'] if 'address_line_1' in address else None
    address_line_2 = address['address_line_2'] if 'address_line_2' in address else None
    city = address['city'] if 'city' in address else None
    state = address['state'] if 'state' in address else None
    zip_code = address['zip_code'] if 'zip_code' in address else None
    country = address['country'] if 'country' in address else None
    return address_line_1, address_line_2, city, state, zip_code, country


@bp.route('', methods=['GET'])
def index():
    customers = Customer.query.all()
    result = [customer.serialize() for customer in customers]
    if len(result) == 0:
        return jsonify('no customers in database')
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    customer = Customer.query.get_or_404(id)
    return jsonify(customer.serialize())


@bp.route('', methods=['POST'])
def create():
    if 'name' not in request.json or 'address' not in request.json:
        return abort(400, 'name or address not provided')
    name = request.json['name']
    if len(name) < 3:
        return abort(400, 'name should be at least 3 characters long')
    address_line_1, address_line_2, city, state, zip_code, country = parse_address_create()
    customer = Customer(
        name=name,
        address_line_1=address_line_1,
        address_line_2=address_line_2,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country
    )
    db.session.add(customer)
    try:
        db.session.commit()
        return jsonify(customer.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    try:
        db.session.commit()
        return jsonify(f'{customer.name} deleted')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PATCH', 'PUT'])
def update(id: int):
    if 'name' not in request.json and 'address' not in request.json:
        return abort(400, 'name or address not provided')
    customer = Customer.query.get_or_404(id)
    if 'name' in request.json:
        name = request.json['name']
        if len(name) < 3:
            return abort(400, 'name should be at least 3 characters long')
        customer.name = name
    if 'address' in request.json:
        address_line_1, address_line_2, city, state, zip_code, country = parse_address_update()
        customer.address_line_1 = address_line_1 if address_line_1 else customer.address_line_1
        customer.address_line_2 = address_line_2 if address_line_2 else customer.address_line_2
        customer.city = city if city else customer.city
        customer.state = state if state else customer.state
        customer.zip_code = zip_code if zip_code else customer.zip_code
        customer.country = country if country else customer.country
    try:
        db.session.commit()
        return jsonify(customer.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/contracts', methods=['GET'])
def customer_contracts(id: int):
    customer = Customer.query.get_or_404(id)
    contracts = Contract.query.filter_by(customer_id=customer.id)
    result = [contract.serialize() for contract in contracts]
    if len(result) == 0:
        return jsonify('customer has no contracts')
    return jsonify(result)


@bp.route('/<int:id>/invoices', methods=['GET'])
def customer_invoices(id: int):
    customer = Customer.query.get_or_404(id)
    invoices = Invoice.query.filter_by(customer_id=customer.id)
    result = [invoice.serialize() for invoice in invoices]
    if len(result) == 0:
        return jsonify('customer has no invoices')
    return jsonify(result)
