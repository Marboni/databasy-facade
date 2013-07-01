import threading
from flask import render_template
from flask import current_app
from flask.ext.mail import Mail, Message

__author__ = 'Marboni'

mail = Mail(current_app)

def create_massege(to_email, subject, template, from_email=None, **kwargs):
    if not from_email:
        from_email = current_app.config['ROBOT_EMAIL']
    if not to_email:
        raise ValueError('Target email not defined.')
    body = render_template(template, site_name=current_app.config['SITE_NAME'], **kwargs)
    subject = subject.encode('utf-8')
    body = body.encode('utf-8')
    return Message(subject, [to_email], body, sender=from_email)


def send(to_email, subject, template, from_email=None, **kwargs):
    message = create_massege(to_email, subject, template, from_email, **kwargs)
    mail.send(message)

def send_async(to_email, subject, template, from_email=None, **kwargs):
    message = create_massege(to_email, subject, template, from_email, **kwargs)
    sender = threading.Thread(target=mail.send, args=(message,))
    sender.start()