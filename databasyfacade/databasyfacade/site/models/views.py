from flask import Blueprint, redirect, url_for, render_template, current_app, request, flash
from flask.ext.login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import NotFound
from databasyfacade.services import models_service
from databasyfacade.site.models.forms import NewModelForm, ModelForm

__author__ = 'Marboni'

bp = Blueprint('models', __name__)

def dashboard():
    if not current_user.is_authenticated():
        return current_app.login_manager.unauthorized()

    own_models = models_service.own_models(current_user.id)
    return render_template('models/dashboard.html',
        own_models=own_models
    )


@bp.route('/new/', methods=['GET', 'POST'])
@login_required
def new_model():
    form = NewModelForm()
    if form.validate_on_submit():
        models_service.create_model(
            form.schema_name.data, form.description.data, form.database_type.data, current_user.id)
        return redirect(url_for('root.home'))
    return render_template('models/new_model.html',
        new_model_form=form
    )


@bp.route('/<int:model_id>/')
@login_required
def model(model_id):
    # Stub to call url_for. This URL will be handled on repo server.
    pass


@bp.route('/<int:model_id>/properties/', methods=['GET', 'POST'])
@login_required
def properties(model_id):
    try:
        model = models_service.model(model_id)
    except NoResultFound:
        raise NotFound

    model_form = ModelForm(obj=model, formdata=request.form)

    if model_form.validate_on_submit():
        models_service.update_model(model_id,
            schema_name=model_form.schema_name.data,
            description=model_form.description.data
        )
        flash('Saved.', 'success')
    return render_template('models/properties.html',
        model=model,
        model_form=model_form,
    )