from fabric.context_managers import lcd
from fabric.operations import local
import os

__author__ = 'Marboni'

FABFILE_DIR = os.path.abspath(os.path.dirname(__file__))

def relative(func):
    def wrapper(*args, **kwargs):
        with lcd(FABFILE_DIR):
            func(*args, **kwargs)
    return wrapper

def local_manage(cmd):
    local('../env/bin/python manage.py %(cmd)s' % {
        'cmd': cmd,
        })

def local_pip(cmd):
    local('../env/bin/pip %(cmd)s' % {
        'cmd': cmd,
        })

@relative
def requirements():
    local_pip('freeze > requirements.txt')

@relative
def requirements_install():
    local_pip('install -r requirements.txt')

@relative
def install(pkg):
    local_pip('install %s' % pkg)
    requirements()

@relative
def uninstall(pkg):
    local_pip('uninstall %s' % pkg)
    requirements()

@relative
def recreatedb(mode=None):
    cmd = 'recreatedb'
    if mode:
        cmd += ' ' + mode
    local_manage(cmd)

@relative
def tests():
    local('../env/bin/nosetests -v')