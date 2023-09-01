from flask import Blueprint, jsonify, abort, request, render_template, redirect, url_for, session
from ..models import db, Customer, Contract, Invoice

bp = Blueprint('customers', __name__, url_prefix='/customers')


def parse_address_create():
    address_line_1 = request.form['address_line_1']
    if not address_line_1:
        abort(400, 'address_line_1 is required')
    address_line_2 = request.form['address_line_2']
    city = request.form['city']
    if not city:
        abort(400, 'city is required')
    state = request.form['state']
    if not state:
        abort(400, 'state is required')
    zip_code = request.form['zip_code']
    if not zip_code:
        abort(400, 'zip_code is required')
    country = request.form['country']
    if not country:
        abort(400, 'country is required')
    return address_line_1, address_line_2, city, state, zip_code, country


def parse_address_update():
    address_line_1 = request.form.get('address_line_1', None)
    address_line_2 = request.form.get('address_line_2', None)
    city = request.form.get('city', None)
    state = request.form.get('state', None)
    zip_code = request.form.get('zip_code', None)
    country = request.form.get('country', None)
    return address_line_1, address_line_2, city, state, zip_code, country


@bp.route('', methods=['GET'])
def index():
    editable_id = session.get('editable_id', None)
    customers = Customer.query.all()
    sorted_customers = sorted(customers, key=lambda x: x.id)
    result = [customer.serialize() for customer in sorted_customers]
    return render_template('customers.html', customers=result, editable_id=editable_id)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    customer = Customer.query.get_or_404(id)
    contracts = Contract.query.filter_by(customer_id=customer.id)
    result = [contract.serialize() for contract in contracts]
    if len(result) == 0:
        return render_template('show_customer.html', customer=customer, contracts=None)
    return render_template('show_customer.html', customer=customer, contracts=contracts)


@bp.route('', methods=['POST'])
def create():
    name = request.form['name']
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return redirect(url_for('customers.index'))


@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id: int):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    try:
        db.session.commit()
        return redirect(url_for('customers.index'))
    except Exception as e:
        print({'error': str(e)}, 'error')
        return redirect(url_for('customers.index'))


@bp.route('/set_editable/<int:id>', methods=['POST'])
def set_editable(id):
    session['editable_id'] = id
    return redirect(url_for('customers.index'))


@bp.route('/udpate/<int:id>', methods=['POST'])
def update(id: int):
    customer = Customer.query.get_or_404(id)
    if 'name' in request.form:
        name = request.form['name']
        if len(name) < 3:
            return abort(400, 'name should be at least 3 characters long')
        customer.name = name
    address_line_1, address_line_2, city, state, zip_code, country = parse_address_update()
    customer.address_line_1 = address_line_1 if address_line_1 else customer.address_line_1
    customer.address_line_2 = address_line_2 if address_line_2 else customer.address_line_2
    customer.city = city if city else customer.city
    customer.state = state if state else customer.state
    customer.zip_code = zip_code if zip_code else customer.zip_code
    customer.country = country if country else customer.country
    session['editable_id'] = None
    try:
        db.session.commit()
        return redirect(url_for('customers.index'))
    except Exception as e:
        print(jsonify({'error': str(e)}), 500)
        return redirect(url_for('customers.index'))


@bp.route('/<int:id>/contracts', methods=['GET'])
def customer_contracts(id: int):
    customer = Customer.query.get_or_404(id)
    contracts = Contract.query.filter_by(customer_id=customer.id)
    result = [contract.serialize() for contract in contracts]
    if len(result) == 0:
        return render_template('show_customer.html', customer=customer, contracts=None)
    return render_template('show_customer.html', customer=customer, contracts=contracts)


@bp.route('/<int:id>/invoices', methods=['GET'])
def customer_invoices(id: int):
    customer = Customer.query.get_or_404(id)
    invoices = Invoice.query.filter_by(customer_id=customer.id)
    result = [invoice.serialize() for invoice in invoices]
    if len(result) == 0:
        return render_template('show_customer.html', customer=customer, invoices=None)
    return render_template('show_customer.html', customer=customer, invoices=result)



