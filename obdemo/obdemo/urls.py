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

from django.conf import settings
from django.conf.urls.defaults import *
from obadmin import admin
import os
admin.autodiscover()

if settings.DEBUG:
    # This stuff can probably go away if/when we switch to Django 1.3,
    # not sure yet how that interacts with django-static.
    urlpatterns = patterns('',
        (r'^(?P<path>(map_icons).*)$',
         'django.views.static.serve', {'document_root': os.path.join(settings.OBDEMO_DIR, 'media')}),
    )
else:
    urlpatterns = patterns('')


urlpatterns += patterns(
    '',

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),

    (r'^disclaimer', 'django.views.generic.simple.direct_to_template',
     {'template': 'disclaimer.html'}),

    (r'^geotagger/$', 'obdemo.views.geotagger_ui'),

    # geotagger api
    (r'^', include('ebdata.geotagger.urls')),

    # ebpub provides nearly all the UI for an openblock site.
    (r'^', include('ebpub.urls')),


)
