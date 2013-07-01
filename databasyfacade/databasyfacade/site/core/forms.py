from datetime import timedelta
from flask import session
from wtforms.ext.csrf.session import SessionSecureForm

__author__ = 'Marboni'

class BaseForm(SessionSecureForm):
    SECRET_KEY = 'uPjvdUVu08k57Znc89V08Q3udpNKz43y'
    TIME_LIMIT = timedelta(minutes=20)

    def __init__(self, formdata=None, obj=None, prefix='', csrf_context=None, **kwargs):
        if not csrf_context:
            csrf_context = session
        SessionSecureForm.__init__(self, formdata, obj, prefix, csrf_context, **kwargs)
