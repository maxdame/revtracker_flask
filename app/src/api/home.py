from flask import Blueprint, render_template, jsonify, request


bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def home():
    return render_template("home.html")
