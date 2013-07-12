import argparse
import sys
from databasyfacade import config

__author__ = 'Marboni'

def recreatedb(mode=None):
    """ Recreates DB.
    mode - application mode: 'development', 'testing', 'staging', 'production'. If None, value will be taken from
    DATABASY_ENV environment variable.
    """
    current_config = config.config_by_mode(mode)
    from databasyfacade.db import recreate_db

    recreate_db(current_config.DATABASE_URI)
    print '\nDatabase recreated: %s.' % current_config.DATABASE_URI


def recreatecache(mode=None):
    """ Recreates cache.
    mode - application mode: 'development', 'testing', 'staging', 'production'. If None, value will be taken from
    DATABASY_ENV environment variable.
    """
    current_config = config.config_by_mode(mode)
    from databasyfacade.cache import recreate_cache

    recreate_cache(current_config.REDIS_URI)
    print '\nCache recreated: %s.' % current_config.REDIS_URI


COMMANDS = {
    'recreatedb': {
        'method': recreatedb,
        'format': 'recreatedb [mode]',
        'help': 'recreates database. Optional parameter \'mode\' takes following values: '
                'development, testing, staging, production.',
    },
    'recreatecache': {
        'method': recreatecache,
        'format': 'recreatecache [mode]',
        'help': 'recreates cache. Optional parameter \'mode\' takes following values: '
                'development, testing, staging, production.',
    }
}

def print_list():
    help = 'Available commands:\n'
    for command, meta in COMMANDS.iteritems():
        help += meta['format'].ljust(40) + ' ' + meta['help'] + '\n'
    print help

parser = argparse.ArgumentParser(description='Executes service commands.')
parser.add_argument('command', metavar='cmd', nargs='?', choices=COMMANDS.keys(), help='command to execute')
parser.add_argument('arguments', metavar='arg', nargs='*', help='parameters of command')
parser.add_argument('-l', '--list', action='store_true', help='prints list of all available commands')

if __name__ == "__main__":
    p = parser.parse_args(sys.argv[1:])
    if p.list:
        print_list()
    elif not p.command:
        print 'Command not specified.\n'
        print_list()
    else:
        command_meta = COMMANDS[p.command]
        command_meta['method'](*p.arguments)