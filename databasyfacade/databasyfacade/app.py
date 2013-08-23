import functools
from logging import StreamHandler, Formatter
import logging
import sys
from flask import Flask, current_app, request
from flask.ext.login import LoginManager
import os
from werkzeug.serving import run_simple
from databasyfacade import config, db, mq
from databasyfacade.auth import load_user
from databasyfacade.context_processor import context_processor
from databasyfacade.utils import mail_sender

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

class PatchedLoginManager(LoginManager):
    def _load_user(self):
        if request.path.startswith(current_app.static_url_path):
            return
        super(PatchedLoginManager, self)._load_user()

def init_login_manager(app):
    login_manager = PatchedLoginManager()
    #noinspection PyTypeChecker
    login_manager.user_loader(load_user)
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.init_app(app)

def init_rpc(app):
    mq.init(app.config['RPC_PORT'], app.config['PUB_PORT'])

def init_mail(app):
    mail_sender.mail.init_app(app)

def create_app():
    app = Flask('databasyfacade')
    app.config.from_object(config.config_by_mode(os.environ.get('DATABASY_ENV')))
    load_modules(app)
    wrap_into_middlewares(app)

    init_logging(app)
    init_context_processor(app)
    init_db(app)
    init_login_manager(app)
    init_rpc(app)
    init_mail(app)

    return app

if __name__ == '__main__':
    app = create_app()
    print 'Server is listening on port %s.' % app.config['PORT']
    run_simple(app.config['HOST'], app.config['PORT'], app,
        use_reloader=False,
        use_debugger=app.debug,
        use_evalex=app.testing
    )

