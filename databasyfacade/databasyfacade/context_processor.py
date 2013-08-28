from flask.ext.login import current_user
from databasyfacade.auth import check_role
from databasyfacade.db.models import ModelRole

__author__ = 'Marboni'

def context_processor(app):
    return {
        'site_name': app.config['SITE_NAME'],
        'current_user': current_user,
        'check_role': check_role,
        'ModelRole': ModelRole,
    }
