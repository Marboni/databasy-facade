from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask.ext.login import logout_user, login_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound
from databasyfacade.services import auth_service, models_service
from databasyfacade.site.auth.forms import LoginForm, SignUpForm

__author__ = 'Marboni'

bp = Blueprint('auth', __name__)

@bp.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated():
        return redirect(url_for('root.home'))

    form = SignUpForm()
    if form.is_submitted():
        if form.validate_on_submit():
            if form.invitation_hex.data:
                try:
                    invitation = models_service.invitation_by_hex(form.invitation_hex.data)
                except NoResultFound:
                    raise NotFound
                if not invitation.active:
                    flash('Sorry, but your invitation has been cancelled.', 'warning')
                    return redirect(url_for('auth.sign_up'))
                profile = auth_service.create_user(form.name.data, invitation.email_lower, form.password.data, True)
                models_service.accept_invitations(profile.user)
                login_user(profile.user, True)
                return redirect(url_for('root.home'))
            else:
                profile = auth_service.create_user(form.name.data, form.email.data, form.password.data, False)
                auth_service.send_activation_mail(profile)
                return render_template('auth/sign_up_completion.html', email=request.form['email'])
    else:
        initial = MultiDict()
        invitation_hex = request.values.get('invitation')
        if invitation_hex:
            try:
                invitation = models_service.invitation_by_hex(invitation_hex)
            except NoResultFound:
                raise NotFound
            else:
                if invitation.active: # Invitation is correct.
                    initial.add('invitation_hex', invitation_hex)
                    initial.add('email', invitation.email_lower)
                else:
                    flash('Sorry, but your invitation has been cancelled.', 'warning')
        form = SignUpForm(formdata=initial)
    return render_template('auth/sign_up.html',
        sign_up_form=form
    )

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('root.home'))

    form = LoginForm(request.values)
    if form.validate_on_submit():
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