from databasyfacade.db import dbs
from databasyfacade.db.models import ModelInfo

__author__ = 'Marboni'

def own_models(user_id):
    """ Returns list of user's models.
    Returns:
       list of user's models.
    """
    return dbs().query(ModelInfo).filter_by(owner_id=user_id).all()

def create_model(schema_name, description, database_type, owner_id):
    """ Creates new model.
    Returns:
       model.
    """
    model = ModelInfo()
    model.schema_name = schema_name
    model.database_type = database_type
    model.description = description
    model.owner_id = owner_id

    dbs().add(model)
    dbs().flush()

    return model

def model(model_id):
    """ Returns model.
    Returns:
       model.
    Raises:
        NoResultFound if profile not found.
    """
    return dbs().query(ModelInfo).filter_by(id=model_id).one()

def delete_model(model_id):
    """ Deletes model.
    Returns:
       removed model.
    Raises:
        NoResultFound if model not found.
    """
    m = model(model_id)
    dbs().delete(m)
    return m