from flask.ext.login import current_user

__author__ = 'Marboni'

def context_processor(app):
    return {
        'site_name': app.config['SITE_NAME'],
        'current_user': current_user
    }
