from wtforms import TextField, validators, SelectField
from databasyfacade.db import models
from flask.ext.wtf import Form

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