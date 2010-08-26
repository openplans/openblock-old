# -*- mode: python ;-*-

import os
import sys
import site

# Some libraries (eg. geopy) have an annoying habit of printing to stdout,
# which is a no-no under mod_wsgi.
# Workaround as per http://code.google.com/p/modwsgi/wiki/ApplicationIssues
sys.stdout = sys.stderr

# This may need to be adjusted based on your installation path.
env_root = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..')
env_root = os.path.abspath(env_root)

sitepackages_root = os.path.join(env_root, 'lib')
for d in os.listdir(sitepackages_root):
    if d.startswith('python'):
      
        site.addsitedir(
         os.path.join(sitepackages_root, d, 'site-packages'))
        break
else:
    raise RuntimeError("Could not find any site-packages to add in %r" % env_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'obdemo.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/obdemo-python-eggs'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

