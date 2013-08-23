import threading
from flask import render_template, copy_current_request_context, current_app
from flask_mail import Mail, Message

__author__ = 'Marboni'

mail = Mail()

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

    @copy_current_request_context
    def send_message(message):
        mail.send(message)

    sender = threading.Thread(name='mail_sender', target=send_message, args=(message,))
    sender.start()