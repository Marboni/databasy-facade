# coding=utf-8
import datetime

__author__ = 'Marboni'

class Config(object):
    DEBUG = False
    TESTING = False

    SITE_NAME = 'Databasy.com'
    DOMAIN = 'databasy.com'
    ENDPOINT = 'http://www.databasy.com'

    MODULES = {
        '': 'databasyfacade.site.root.views',
        '/auth': 'databasyfacade.site.auth.views',
        '/models': 'databasyfacade.site.models.views',
        }

    MIDDLEWARES = (
        'databasyfacade.middlewares.DbSessionMiddleware',
    )

    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = None
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)

    HOST = ''
    PORT = 5000

    CSRF_ENABLED = True

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy'
    DATABASE_ECHO = True

    RPC_PORT = 5555
    PUB_PORT = 5556

    SECRET_KEY = 'yxS3bDAEOF60OibRXbO5rcMUG6cyNezEwrQMKgsg'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'bmarchenko@databasy.com'
    MAIL_PASSWORD = 'Todotowin1099'

    ROBOT_EMAIL = 'Databasy.com <bmarchenko@databasy.com>'

class DevelopmentConfig(Config):
    ENV = 'development'

    DEBUG = True
    DOMAIN = 'databasy'
    ENDPOINT = 'http://databasy'

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_development'

class TestingConfig(Config):
    ENV = 'testing'

    TESTING = True

    DOMAIN = 'databasy'
    ENDPOINT = 'http://databasy'

    CSRF_ENABLED = False

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_testing'

    RPC_PORT = 6666
    PUB_PORT = 6667


class StagingConfig(Config):
    ENV = 'staging'

    DOMAIN = 'databasy'
    ENDPOINT = 'http://databasy'

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_staging'

class ProductionConfig(Config):
    ENV = 'production'

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_production'

CONFIGS = [
    DevelopmentConfig,
    TestingConfig,
    StagingConfig,
    ProductionConfig
]
DEFAULT_CONFIG = DevelopmentConfig

def config_by_mode(config_mode):
    if not config_mode:
        return DEFAULT_CONFIG
    else:
        for config in CONFIGS:
            if config_mode == config.ENV:
                return config
        else:
            raise ValueError('Profile "%s" not defined. Check DATABASY_ENV environment variable.' % config_mode)