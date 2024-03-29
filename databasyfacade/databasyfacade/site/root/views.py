from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required
from databasyfacade.services import auth_service
from databasyfacade.site.models.views import dashboard
from databasyfacade.site.auth.forms import SignUpForm

__author__ = 'Marboni'

bp = Blueprint('root', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated():
        return dashboard()

    form = SignUpForm()
    if form.validate_on_submit():
        profile = auth_service.create_user(form.username.data, form.email.data, form.password.data, False)
        auth_service.send_activation_mail(profile)
        return render_template('auth/sign_up_completion.html', email=form.email.data)
    return render_template('root/welcome.html',
        sign_up_form=form
    )

@bp.route('/secure/')
@login_required
def secure():
    # Used for testing purpose.
    return 'OK'