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

from paste.script import templates
from paste.script.templates import var

def _random_string(length=12):
    import random
    import string
    result = ''
    for i in range(length):
        result += random.choice(string.letters + string.digits)
    return result

class OpenblockTemplate(templates.Template):
    """
    A template for the ``paster create`` command that
    bootstraps a custom OpenBlock Django app as described in
    the OpenBlock `custom app` docs.
    """
    required_templates = []
    use_cheetah = False
    summary = "Basic OpenBlock project template"
    _template_dir = 'project_templates/openblock'

    vars = [
        var('password_salt',
            'Salt used to hash passwords',
            default=_random_string()),
        var('reset_salt',
            'Salt used to hash password resets',
            default=_random_string()),
        var('staff_cookie_val',
            'Secret cookie value used to identify staff',
            default=_random_string()),
        var('description',
            'project description',
            default='A Django app that provides a custom OpenBlock site'),
        var('author',
            'Your name for the package metadata',
            ),
        var('author_email',
            'Your email for the package metadata',
            ),
        var('license',
            'License',
            default='GPLv3',
            ),

    ]

    def post(self, command, output_dir, vars):
        """Make some files executable. Pastescript forgets to do so,
        see issue https://bitbucket.org/ianb/pastescript/issue/2/executable-files-in-templates-do-not-have
        """
        if command.command_name == 'create':
            # not sure if there's a better thing to check.
            import os.path
            package_dir = os.path.join(output_dir, vars['project'])
            for fname in ('manage.py', 'manage.sh'):
                f = os.path.join(package_dir, fname)
                os.chmod(f, 0770)
