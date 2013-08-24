from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.db import dbs
from databasyfacade.db.auth import User, Profile
from databasyfacade.db.models import ModelInfo, ModelRole, Invitation

__author__ = 'Marboni'

def create_model(schema_name, description, database_type, owner_id):
    """ Creates new model.
    Returns:
       model.
    """
    model = ModelInfo()
    model.schema_name = schema_name
    model.database_type = database_type
    model.description = description

    dbs().add(model)
    dbs().flush()

    owner_role = ModelRole()
    owner_role.model_id = model.id
    owner_role.user_id = owner_id
    owner_role.role = ModelRole.OWNER

    dbs().add(owner_role)
    dbs().flush()

    return model

def model(model_id):
    """ Returns model.
    Returns:
       model.
    Raises:
        NoResultFound if profile not found.
    """
    return dbs().query(ModelInfo).filter_by(id=model_id).one()

def update_model(model_id, **kwargs):
    """ Updates properties of the model.
    Parameters:
        model_id - ID of model to update.
        kwargs - keys and values of properties to update.
    Raises:
        NoResultFound if model not found.
    """
    updated = dbs().query(ModelInfo).filter_by(id=model_id).update(kwargs, synchronize_session=False)
    if not updated:
        raise NoResultFound

def delete_model(model_id):
    """ Deletes model.
    Returns:
       removed model.
    Raises:
        NoResultFound if model not found.
    """
    dbs().query(Invitation).filter_by(model_id=model_id, active=True).update({'active': False}, synchronize_session=False)
    dbs().expire_all()
    m = model(model_id)
    dbs().delete(m)
    return m

def user_roles(user_id):
    """ Returns list of user roles.
    Returns:
       list of user's roles with joined models.
    """
    return dbs().query(ModelRole).join(ModelInfo).filter(ModelRole.user_id == user_id).all()

def model_roles(model_id):
    """ Returns roles of users in model with joined profiles.
    Parameters:
        model_id - model ID.
    Returns:
        list of roles with joined users.
    """
    return dbs().query(ModelRole).join(User).join(Profile)\
    .filter(ModelRole.model_id == model_id)\
    .order_by(ModelRole.role, Profile.name)\
    .all()

def role(model_id, user_id):
    """ Returns role.
    Returns:
       role.
    Raises:
        NoResultFound if role not found.
    """
    return dbs().query(ModelRole).filter_by(model_id=model_id, user_id=user_id).one()

def delete_role(model_id, user_id):
    """ Deletes role.
    Raises:
        NoResultFound if role not found.
        ValueError if role is Owner.
    Returns:
        removed role with joined user and profile.
    """
    role = dbs().query(ModelRole).join(User).join(Profile).filter(ModelRole.model_id==model_id, ModelRole.user_id==user_id).one()
    if role.role == ModelRole.OWNER:
        raise ValueError('Unable to delete role "Owner".')
    dbs().delete(role)
    return role

def join_to_model(target_model, inviting_user, users, role):
    """ Joins existing users to the model, creating roles and sending notifications to email.
    """
    for user in users:
        model_role = ModelRole()
        model_role.model_id = target_model.id
        model_role.user_id = user.id
        model_role.role = role
        dbs().add(model_role)

        from flask import current_app

        topic = '%s shared model with you on %s' % (inviting_user.profile.name, current_app.config['SITE_NAME'])

        user.profile.send_mail_async(topic, 'mails/invitation_notification.txt',
            user_name=user.profile.name,
            inviting_user_name=inviting_user.profile.name,
            inviting_user_email=inviting_user.profile.email,
            schema_name=target_model.schema_name
        )
    dbs().flush()


def invite_to_model(target_model, inviting_user, emails, role, sign_up_url):
    """ Invite new people to become part of model's team, sending them letters with link, that allows sign up and join team.
    """
    for email in emails:
        invitation = Invitation(target_model.id, email, role)
        dbs().add(invitation)

        from flask import current_app

        topic = '%s shared model with you on %s' % (inviting_user.profile.name, current_app.config['SITE_NAME'])
        sign_up_link = '%s/?invitation=%s' % (sign_up_url.rstrip('/'), invitation.hex)

        from databasyfacade.utils import mail_sender
        mail_sender.send_async(email, topic, 'mails/invitation.txt',
            inviting_user_name=inviting_user.profile.name,
            inviting_user_email=inviting_user.profile.email,
            schema_name=target_model.schema_name,
            sign_up_link=sign_up_link
        )
    dbs().flush()

def accept_invitations(user):
    """ Search active user's invitations, creates roles to the models by them, then deletes invitations.
    """
    models_and_roles = dbs().query(Invitation).filter_by(
        email_lower=user.email_lower, active=True
    ).values('model_id', 'role')
    for model_id, role in models_and_roles:
        model_role = ModelRole()
        model_role.model_id = model_id
        model_role.user_id = user.id
        model_role.role = role
        dbs().add(model_role)
    dbs().flush()
    delete_invitations(user.email_lower)

def delete_invitations(email):
    """ Deletes invitation.
    Returns:
        number of removed invitations.
    """
    return dbs().query(Invitation).filter_by(email_lower=email.lower()).delete()

def invitation_by_hex(invitation_hex):
    """ Returns invitation by hex.
    Raises:
        NoResultFound if no invitation with specific ID or HEX found.
    """
    return dbs().query(Invitation).filter_by(hex=invitation_hex).one()

def invitations_by_model(model_id):
    """ Returns active invitations to specific model.
    Returns:
        list of invitations.
    """
    return dbs().query(Invitation).filter_by(model_id=model_id).all()

def invitations_by_email(email):
    """ Returns invitations for specific email.
    Returns:
        list of invitations.
    """
    return dbs().query(Invitation).filter_by(email_lower=email.lower()).all()
#
#
#def update_invitation(invitation_id, **kwargs):
#    """ Updates properties of the invitation.
#Parameters:
#invitation_id - ID of invitation to update.
#kwargs - keys and values of properties to update.
#Raises:
#NoResultFound if unable to find invitation to update.
#"""
#    updated = dbs().query(Invitation).filter_by(id=invitation_id).update(kwargs, synchronize_session=False)
#    if not updated:
#        raise NoResultFound
#
#
#def delete_invitations(email):
#    """ Deletes invitation.
#Returns:
#number of removed invitations.
#"""
#    return dbs().query(Invitation).filter_by(email_lower=email.lower()).delete()