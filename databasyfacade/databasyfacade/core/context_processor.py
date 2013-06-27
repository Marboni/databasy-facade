__author__ = 'Marboni'

def context_processor(app):
    return {
        'site_name': app.config['SITE_NAME']
    }
