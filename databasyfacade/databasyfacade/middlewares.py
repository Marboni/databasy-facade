from databasyfacade.db import dbs, remove_session

__author__ = 'Marboni'

class DbSessionMiddleware:
    def __init__(self, flask_app):
        self.app = flask_app.wsgi_app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except BaseException:
            dbs().rollback()
            raise
        finally:
            dbs().commit()
            remove_session()