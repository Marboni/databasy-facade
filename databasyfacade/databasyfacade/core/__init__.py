from flask import Blueprint, render_template

__author__ = 'Marboni'

bp = Blueprint('core', __name__)

@bp.route('/')
def home():
    return render_template('core/welcome.html')
