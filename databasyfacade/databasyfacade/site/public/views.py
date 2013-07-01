from flask import Blueprint, request, render_template, redirect, url_for, current_app
from flask.ext.login import login_required, login_user, current_user
from databasyfacade.services import auth_service
from databasyfacade.site.auth.forms import SignUpForm, LoginForm

__author__ = 'Marboni'

bp = Blueprint('public', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated():
        return redirect('/secure')

    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        user = auth_service.create_user(request.form['name'], request.form['email'], request.form['password'], False)
        auth_service.send_activation_mail(user)
        return render_template('auth/sign_up_completion.html', email=request.form['email'])
    return render_template('public/welcome.html',
        sign_up_form=form
    )

@bp.route('/secure/')
@login_required
def secure():
    return render_template('public/secure.html')