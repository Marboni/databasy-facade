from flask import Blueprint, request, redirect, url_for, render_template, current_app
from flask.ext.login import login_required, current_user
from databasyfacade.services import models_service
from databasyfacade.site.models.forms import NewModelForm

__author__ = 'Marboni'

bp = Blueprint('models', __name__)

def dashboard():
    if not current_user.is_authenticated():
        return current_app.login_manager.unauthorized()

    own_models = models_service.own_models(current_user.id)
    return render_template('models/dashboard.html',
        own_models = own_models
    )

@bp.route('/new/', methods=['GET', 'POST'])
@login_required
def new_model():
    form = NewModelForm(request.form)
    if request.method == 'POST' and form.validate():
        models_service.create_model(
            form.schema_name.data, form.description.data, form.database_type.data, current_user.id)
        return redirect(url_for('root.home'))
    return render_template('models/new_model.html',
        new_model_form = form
    )