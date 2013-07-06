from wtforms import TextField, validators, SelectField
from databasyfacade.db import models
from databasyfacade.site.core.forms import BaseForm

__author__ = 'Marboni'

class NewModelForm(BaseForm):
    schema_name = TextField('Schema name', [
        validators.Length(min=1, max=128)
    ], id='nmf_schema_name')

    description = TextField('Description', [
        validators.Length(max=1024)
    ], id='nmf_description')

    database_type = SelectField('Database type',
        choices=models.DB_TYPES,
        id='nmf_database_type')