# This code derived from django-apikey by
# Steve Scoursen and Jorge Eduardo Cardona,
# http://pypi.python.org/pypi/django-apikey
# BSD license.

# XXX TODO delete this?

from django.forms import ModelForm
from .models import ApiKey

class KeyForm( ModelForm ):
    class Meta:
        model = ApiKey
        exclude = ( 'user', )
