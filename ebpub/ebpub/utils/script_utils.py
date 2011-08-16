#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Utils for command-line scripts.
"""

from django.core.management.base import CommandError
from ebpub.utils.logutils import log_exception
import os
import subprocess
import zipfile

def die(msg):
    """
    Useful in places where you can't syntactically put 'raise CommandError'.
    Eg. ``do_something() or die('oops')``
    """
    raise CommandError(msg)

def makedirs(path):
    """Emulates the `mkdir -p` shell command.
    """
    if os.path.exists(path):
        return True
    try:
        os.makedirs(path)
        return True
    except:
        log_exception()
        return False

def shell_command(cmd, args="", cwd=None):
    """Quick hack to replace a single bash command from existing shell scripts.
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(cwd or old_cwd)
        status = subprocess.call("%s %s" % (cmd, args), shell=True)
        return status == 0
    finally:
        os.chdir(old_cwd)

def wget(url, cwd=None, options="-N"):
    """Quick hack to invoke wget from python scripts.
    """
    # We could use httlib2, but meh, that's a bit more work.
    return shell_command('wget', args='%s %s' % (options, url), cwd=cwd)

def unzip(filename, cwd=None):
    """Unzip filename, write extracted files into cwd (default is the current dir).
    """
    try:
        zfile = zipfile.ZipFile(filename)
        zfile.extractall(path=cwd)
        return True
    except:
        log_exception()
        return False

