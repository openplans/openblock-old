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

from ebpub.settings_default import *

OBDEMO_DIR = os.path.normpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (os.path.join(OBDEMO_DIR, 'templates'), ) + TEMPLATE_DIRS
ROOT_URLCONF = 'obdemo.urls'

print "****************************************************************************"
print "* Warning! obdemo.setting_default is deprecated in favor of "
print "* ebpub.settings_default"
print "* "
print "* Please modify your settings.py to import ebpub.settings_default instead."
print "* You will also need to provide values for ROOT_URLCONF, OBDEMO_DIR"
print "* and include the obdemo templates in your template path, eg:"
print "* "
print "* from ebpub.settings_default import *"
print "* OBDEMO_DIR = os.path.normpath(os.path.dirname(__file__))"
print "* TEMPLATE_DIRS = (os.path.join(OBDEMO_DIR, 'templates'), ) + TEMPLATE_DIRS"
print "* ROOT_URLCONF = 'obdemo.urls'"
print "****************************************************************************"