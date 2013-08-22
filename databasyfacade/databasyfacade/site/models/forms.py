import re
from wtforms import TextField, validators, SelectField, ValidationError, TextAreaField
from wtforms.widgets import TextArea
from databasyfacade.db import models
from flask.ext.wtf import Form
from databasyfacade.db.models import ModelRole

__author__ = 'Marboni'

class ModelForm(Form):
    schema_name = TextField('Schema name', [
        validators.Length(min=1, max=128)
    ], id='nmf_schema_name')

    description = TextField('Description', [
        validators.Length(max=1024)
    ], id='nmf_description')

class NewModelForm(ModelForm):
    database_type = SelectField('Database type',
        choices=models.DB_TYPES,
        id='nmf_database_type')

class InviteForm(Form):
    emails = TextAreaField('Emails', [
        validators.Length(min=3, max=1024)
    ], id='if_emails')

    role = SelectField('Role',
        choices=[role for role in ModelRole.ROLES if role[0] != ModelRole.OWNER],
        id='if_role'
    )

    def validate_emails(self, field):
        emails = [email.strip() for email in field.data.split(',')]
        wrong_emails = []
        correct_email_found = False
        for email in emails:
            if not email:
                continue
            if not re.match('.+@.+\..+', email):
                wrong_emails.append(email)
            else:
                correct_email_found = True
        if wrong_emails:
            if len(wrong_emails) == 1:
                raise ValidationError('Email %s is invalid.' % wrong_emails[0])
            else:
                raise ValidationError('Following emails are invalid: %s.' % ', '.join(wrong_emails))
        elif not correct_email_found:
            raise ValidationError('Please enter at least one email.')
