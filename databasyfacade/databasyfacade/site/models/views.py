from flask import Blueprint, redirect, url_for, render_template, current_app, request, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized
from databasyfacade.auth import has_role, check_role
from databasyfacade.db.models import ModelRole
from databasyfacade.services import models_service, auth_service
from databasyfacade.services.errors import OwnerRoleModificationException
from databasyfacade.site.models.forms import NewModelForm, ModelForm, InviteForm

__author__ = 'Marboni'

bp = Blueprint('models', __name__)

def dashboard():
    if not current_user.is_authenticated():
        return current_app.login_manager.unauthorized()

    roles = models_service.user_roles(current_user.id)
    owner_roles = [role for role in roles if role.role == ModelRole.OWNER]
    member_roles = [role for role in roles if role.role != ModelRole.OWNER]
    return render_template('models/dashboard.html',
        owner_roles=owner_roles,
        member_roles=member_roles
    )


@bp.route('/new/', methods=['GET', 'POST'])
@login_required
def new_model():
    form = NewModelForm()
    if form.validate_on_submit():
        models_service.create_model(
            form.schema_name.data, form.description.data, form.database_type.data, current_user.id)
        return redirect(url_for('root.home'))
    return render_template('models/new_model.html',
        new_model_form=form
    )


@bp.route('/<int:model_id>/')
@login_required
def model(model_id):
    # Stub to call url_for. This URL will be handled on repo server.
    pass


@bp.route('/<int:model_id>/properties/', methods=['GET', 'POST'])
@has_role(ModelRole.VIEWER)
def properties(model_id):
    try:
        model = models_service.model(model_id)
    except NoResultFound:
        raise NotFound

    form = ModelForm(obj=model)

    if form.validate_on_submit():
        if not check_role(model_id, ModelRole.DEVELOPER):
            raise Unauthorized
        models_service.update_model(model_id,
            schema_name=form.schema_name.data,
            description=form.description.data
        )
        flash('Saved.', 'success')
    return render_template('models/properties.html',
        model=model,
        model_form=form,
    )


@bp.route('/<int:model_id>/team/', methods=['GET'])
@has_role(ModelRole.VIEWER)
def team(model_id):
    try:
        model = models_service.model(model_id)
    except NoResultFound:
        raise NotFound

    model_roles = models_service.model_roles(model_id)
    invitations = models_service.active_invitations_by_model(model_id)

    member_roles = [role for role in ModelRole.ROLES if role[0] != ModelRole.OWNER]

    return render_template('models/team.html',
        model=model,
        model_roles=model_roles,
        invitations=invitations,
        member_roles=member_roles
    )


@bp.route('/<int:model_id>/team/invite/', methods=['GET', 'POST'])
@has_role(ModelRole.OWNER)
def invite(model_id):
    try:
        model = models_service.model(model_id)
    except NoResultFound:
        raise NotFound

    form = InviteForm(request.form)
    if form.validate_on_submit():
        emails = set((email.strip().lower() for email in form.emails.data.split(',')))
        role = form.role.data

        model_roles = models_service.model_roles(model_id)
        model_emails = set(role.user.email_lower for role in model_roles)

        # Remove team members emails.
        emails = emails - model_emails
        if emails:
            invitations_count = len(emails)

            # Remove emails of people that were invited before.
            existing_invitations = models_service.active_invitations_by_model(model_id)
            existing_invitation_emails = set(
                (existing_invitation.email_lower for existing_invitation in existing_invitations if existing_invitation.active)
            )
            emails = emails - existing_invitation_emails

            if emails:
                # Users that have no permissions to model, but registered on site.
                existing_users = auth_service.users_by_email(emails)
                if existing_users:
                    models_service.join_to_model(model, current_user, existing_users, role)

                    existing_user_emails = set((user.email_lower for user in existing_users))
                    emails = emails - existing_user_emails

                # Only not registered emails left in emails set.
                sign_up_link = current_app.config['ENDPOINT'] + url_for('auth.sign_up')
                models_service.invite_to_model(model, current_user, emails, role, sign_up_link)

            if invitations_count == 1:
                message = 'New member invited.'
            else:
                message = 'New members invited.'
            flash(message, 'success')

            return redirect(url_for('models.team', model_id=model_id))
        else:
            flash('All email owners are the team members.', 'warning')

    return render_template('models/invite.html',
        model=model,
        invite_form=form
    )


@bp.route('/<int:model_id>/team/give-up/')
@login_required
def give_up(model_id):
    # Stub to call url_for. This URL will be handled on repo server.
    pass


@bp.route('/<int:model_id>/team/<int:user_id>/remove/')
@has_role(ModelRole.OWNER)
def remove_member(model_id, user_id):
    try:
        removed_role = models_service.delete_role(model_id, user_id)
    except NoResultFound:
        raise NotFound
    except OwnerRoleModificationException:
        raise BadRequest
    flash('You have removed %s from the team.' % removed_role.user.username, 'success')
    return redirect(url_for('models.team', model_id=model_id))


@bp.route('/<int:model_id>/team/invitations/<int:invitation_id>/remove/')
@has_role(ModelRole.OWNER)
def cancel_invitation(model_id, invitation_id):
    try:
        invitation = models_service.invitation(invitation_id)
        if invitation.model_id != model_id or not invitation.active:
            raise NotFound
        models_service.update_invitation(invitation_id, active=False)
    except NoResultFound:
        raise NotFound
    flash('You have cancelled the invitation sent to %s.' % invitation.email_lower, 'success')
    return redirect(url_for('models.team', model_id=model_id))


@bp.route('/<int:model_id>/team/<int:user_id>/', methods=['POST'])
@has_role(ModelRole.OWNER)
def change_member_role(model_id, user_id):
    role = request.form['role']
    try:
        models_service.update_role(model_id, user_id, role)
    except NoResultFound:
        raise NotFound
    except OwnerRoleModificationException:
        raise BadRequest
    return 'OK'

@bp.route('/<int:model_id>/team/invitations/<int:invitation_id>/', methods=['POST'])
@has_role(ModelRole.OWNER)
def change_invitation_role(model_id, invitation_id):
    role = request.form['role']
    if role not in (ModelRole.VIEWER, ModelRole.DEVELOPER):
        raise BadRequest
    try:
        invitation = models_service.invitation(invitation_id)
        if invitation.model_id != model_id or not invitation.active:
            raise NotFound
        models_service.update_invitation(invitation_id, role=role)
    except NoResultFound:
        raise NotFound
    return 'OK'