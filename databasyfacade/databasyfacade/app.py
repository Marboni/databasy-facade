import functools
from logging import StreamHandler, Formatter
import logging
import sys
from flask import Flask
from flask.ext.login import LoginManager
import os
from werkzeug.serving import run_simple
from databasyfacade import config, db
from databasyfacade.auth import load_user
from databasyfacade.context_processor import context_processor

__author__ = 'Marboni'

def load_modules(app):
    try:
        modules = app.config['MODULES']
    except KeyError:
        raise Exception('Key MODULES not found in your configuration.')
    for prefix, module_name in modules.iteritems():
        try:
            module = __import__(module_name, fromlist=['bp'])
        except ImportError, e:
            raise ImportError('Unable to load module %s: %s.' % (module_name, e.message))
        try:
            app.register_blueprint(module.bp, url_prefix=prefix)
        except AttributeError:
            raise AttributeError('Module %s has no required attribute bp.' % module_name)


def wrap_into_middlewares(app):
    for middleware_name in reversed(app.config['MIDDLEWARES']):
        module_name, clazz_name = middleware_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=[clazz_name])
        app.wsgi_app = getattr(module, clazz_name)(app)


def init_logging(app):
    if not app.debug:
        stderr_handler = StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        app.logger.addHandler(stderr_handler)

def init_context_processor(app):
    #noinspection PyUnusedLocal
    app.template_context_processors[None].append(functools.partial(context_processor, app))

def init_db(app):
    db.init_engine(app.config['DATABASE_URI'], echo=app.config['DATABASE_ECHO'])

def init_login_manager(app):
    login_manager = LoginManager()
    #noinspection PyTypeChecker
    login_manager.user_loader(load_user)
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.init_app(app)

def create_app():
    app = Flask('databasyfacade')
    app.config.from_object(config.config_by_mode(os.environ.get('DATABASY_ENV')))
    load_modules(app)
    wrap_into_middlewares(app)

    init_logging(app)
    init_context_processor(app)
    init_db(app)
    init_login_manager(app)

    return app

app = create_app()

if __name__ == '__main__':
    print 'Server is listening on port %s.' % app.config['PORT']
    run_simple(app.config['HOST'], app.config['PORT'], app,
        use_reloader=False,
        use_debugger=app.debug,
        use_evalex=app.testing
    )

