from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask.ext.login import login_required, logout_user, login_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.services import auth_service
from databasyfacade.site.auth.forms import LoginForm

__author__ = 'Marboni'

bp = Blueprint('auth', __name__)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('root.home'))

    form = LoginForm(request.values)
    if request.method == 'POST' and form.validate():
        try:
            user = auth_service.user_by_email(form.email.data)
        except NoResultFound:
            form.email.errors = ['User with this email doesn\'t exist.']
        else:
            if user.is_active():
                if user.check_password(form.password.data):
                    login_user(user, form.remember_me.data)
                    redirect_to = form.next.data or url_for('root.home')
                    return redirect(redirect_to)
                else:
                    form.password.errors = ['Incorrect password.']
            else:
                form.email.errors = ['This email address is not confirmed.']
    return render_template('auth/login.html',
        login_form=form
    )


@bp.route('/activate/')
def activate():
    user = auth_service.activate_user(request.args.get('token'))
    if user:
        login_user(user, True)
        flash('Welcome!', 'success')
        return redirect(url_for('root.home'))
    else:
        logout_user()
        flash('''Email confirmation token does not exist. There are two possible causes:
            <ul>
            <li>
                <b>Your email address is already confirmed.</b> Use this form to log in.
            </li>
            <li>
                <b>Link is incorrect.</b> Make sure that address bar of your browser contains URL from confirmation letter.
            </li>
            </ul>
            ''', 'warning')
        return render_template('auth/login.html',
            login_form=LoginForm()
        )


@bp.route('/logout/')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return redirect(url_for('root.home'))