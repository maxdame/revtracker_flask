from datetime import datetime
from flask import request
from flask import Blueprint, jsonify, request
from ..models import Invoice, Transaction, invoices_transactions
from collections import defaultdict
from dateutil.relativedelta import relativedelta


bp = Blueprint('accountant_tools', __name__, url_prefix='/accountant-tools')


@bp.route('/revenue-by-product', methods=['GET'])
def revenue_by_product():
    start_date_request = request.json['start_date']
    end_date_request = request.json['end_date']

    # Convert dates to datetime objects
    start_date = datetime.strptime(
        start_date_request, '%Y-%m-%d') if start_date_request else None
    end_date = datetime.strptime(
        end_date_request, '%Y-%m-%d') if end_date_request else None

    # Adjust query based on provided dates
    query = Invoice.query.join(invoices_transactions).join(Transaction)
    if start_date:
        query = query.filter(Invoice.date >= start_date)
    if end_date:
        query = query.filter(Invoice.date <= end_date)

    invoices = query.all()

    revenue_by_product = defaultdict(float)

    for invoice in invoices:
        for transaction in invoice.transactions:
            product = transaction.product.name
            start_date = transaction.start_date
            end_date = transaction.end_date
            num_of_months = relativedelta(end_date, start_date).months + 1
            print('----------------------------')
            print('PRODUCT:', product)
            print('NUMBER OF MONTHS:', num_of_months)
            print('TRANS VAL:', transaction.value)
            print('MONTHLY AMT:', transaction.value / num_of_months)
            print('----------------------------')
            revenue_by_product[product] += transaction.value / num_of_months

    return jsonify(revenue_by_product)
