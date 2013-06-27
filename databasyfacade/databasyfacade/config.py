# coding=utf-8

__author__ = 'Marboni'

class Config(object):
    DEBUG = False
    TESTING = False

    SITE_NAME = 'Databasy.com'

    MODULES = {
        '/': 'databasyfacade.core',
        '/auth': 'databasyfacade.auth',
        }

    MIDDLEWARES = ()

    HOST = ''
    PORT = 5000

    SECRET_KEY = 'yxS3bDAEOF60OibRXbO5rcMUG6cyNezEwrQMKgsg'

class DevelopmentConfig(Config):
    ENV = 'development'

    DEBUG = True


class TestingConfig(Config):
    ENV = 'testing'


class StagingConfig(Config):
    ENV = 'staging'


class ProductionConfig(Config):
    ENV = 'production'


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