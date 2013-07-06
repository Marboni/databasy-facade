# coding=utf-8

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

    HOST = ''
    PORT = 5000

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy'
    DATABASE_ECHO = True

    SECRET_KEY = 'yxS3bDAEOF60OibRXbO5rcMU'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'bmarchenko@databasy.com'
    MAIL_PASSWORD = 'Todotowin'

    ROBOT_EMAIL = 'Databasy.com <bmarchenko@databasy.com>'

class DevelopmentConfig(Config):
    ENV = 'development'

    DEBUG = True
    DOMAIN = 'databasy'
    ENDPOINT = 'http://databasy'

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_development'

class TestingConfig(Config):
    ENV = 'testing'

    DOMAIN = 'databasy'
    ENDPOINT = 'http://databasy'

    DATABASE_URI = 'postgresql://postgres:postgres@localhost/databasy_testing'


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