from ebpub.settings_default import *

OBDEMO_DIR = os.path.normpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (os.path.join(OBDEMO_DIR, 'templates'), ) + TEMPLATE_DIRS
ROOT_URLCONF = 'obdemo.urls'

print "****************************************************************************"
print "* Warning! obdemo.setting_default.py is deprecated in favor of "
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