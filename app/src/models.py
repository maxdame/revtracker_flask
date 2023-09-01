
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum


db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    created_on = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    address_line_1 = db.Column(db.String(200), nullable=False)
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    def __init__(self, name, address_line_1, address_line_2, city, state, zip_code, country):
        self.name = name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def serialize(self):
        return {
            'customer_id': self.id,
            'name': self.name,
            'created_on': self.created_on.strftime('%Y-%m-%d'),
            'is_active': self.is_active,
            'address': {
                'address_line_1': self.address_line_1,
                'address_line_2': self.address_line_2,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'country': self.country,
            }
        }


class ProductType(enum.Enum):
    rfq = 'request for quote'
    implementation = 'implementation'
    core = 'core subscription'
    fullsuite = 'fullsuite subscription'
    # fs_step_up = 'fullsuite step up'
    # discount = 'discount'


class BillingCadence(enum.Enum):
    monthly = 'monthly'
    quarterly = 'quarterly'
    annually = 'annually'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Enum(ProductType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    billing_cadence = db.Column(
        db.Enum(BillingCadence), default=BillingCadence.monthly, nullable=False)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('contracts.id', ondelete='NO ACTION'),
        nullable=False,
        index=True)
    contract = db.relationship('Contract', backref=db.backref('transactions'))

    def __init__(self, product, value, start_date, end_date, billing_cadence, contract_id):
        self.product = product
        self.value = value
        self.start_date = start_date
        self.end_date = end_date
        self.billing_cadence = billing_cadence
        self.contract_id = contract_id

    def serialize(self):
        return {
            'transaction_id': self.id,
            'customer_name': self.contract.customer.name,
            'contract_id': self.contract_id,
            'product': self.product.name,
            'value': self.value,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'billing_cadence': self.billing_cadence.name,
        }


class ContractStatus(enum.Enum):
    draft = 'draft'
    pending = 'pending'
    active = 'active'
    expired = 'expired'
    cancelled = 'cancelled'
    renewed = 'renewed'
    upgraded = 'upgraded'


class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.Enum(ContractStatus),
        default=ContractStatus.draft,
        nullable=False)
    created_on = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id', ondelete='NO ACTION'),
        nullable=False,
        index=True)
    customer = db.relationship('Customer', backref=db.backref('contracts'))

    def __init__(self, start_date, end_date, value, status, customer_id):
        self.start_date = start_date
        self.end_date = end_date
        self.value = value
        self.status = status
        self.customer_id = customer_id

    def serialize(self):
        formatted_value = "{:,.2f}".format(self.value)
        return {
            'contract_id': self.id,
            'created_on': self.created_on,
            'customer_name': self.customer.name,
            'status': self.status.name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'value': formatted_value
        }


invoices_transactions = db.Table(
    'invoice_transactions',
    db.Column('invoice_id', db.Integer, db.ForeignKey('invoices.id'),
              primary_key=True),
    db.Column('transaction_id', db.Integer, db.ForeignKey('transactions.id'),
              primary_key=True))


class PaymentTerms(enum.Enum):
    due_upon_receipt = 'due upon receipt'
    net_7 = 'net 7'
    net_15 = 'net 15'
    net_30 = 'net 30'


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    payment_terms = db.Column(
        db.Enum(PaymentTerms),
        default=PaymentTerms.due_upon_receipt,
        nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id', ondelete='NO ACTION'),
        nullable=False,
        index=True)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('contracts.id', ondelete='NO ACTION'),
        nullable=False,
        index=True)
    customer = db.relationship('Customer', backref=db.backref('customer'))
    contract = db.relationship('Contract', backref=db.backref('contract'))
    transactions = db.relationship(
        'Transaction', secondary=invoices_transactions, backref=db.backref('transactions'))

    def __init__(self, date, payment_terms, customer_id, contract_id, amount_due):
        self.date = date
        self.payment_terms = payment_terms
        self.amount_due = amount_due
        self.customer_id = customer_id
        self.contract_id = contract_id

    def serialize(self):
        return {
            'invoice_id': self.id,
            'customer_id': self.customer_id,
            'contract_id': self.contract_id,
            'invoice_date': self.date.strftime('%Y-%m-%d'),
            'payment_terms': self.payment_terms.name,
            'amount_due': self.amount_due
        }
