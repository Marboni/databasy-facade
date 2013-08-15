from databasyfacade.db import dbs
from databasyfacade.db.models import ModelInfo

__author__ = 'Marboni'

def own_models(user_id):
    return dbs().query(ModelInfo).filter_by(owner_id=user_id).all()

def create_model(schema_name, description, database_type, owner_id):
    model = ModelInfo()
    model.schema_name = schema_name
    model.database_type = database_type
    model.description = description
    model.owner_id = owner_id

    dbs().add(model)
    dbs().flush()

    return model

def model(model_id):
    return dbs().query(ModelInfo).get(model_id)
