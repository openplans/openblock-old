#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebblog
#
#   ebblog is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebblog is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebblog.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.admin import ModelAdmin, site
from ebblog.blog.models import Entry

class EntryAdmin(ModelAdmin):
    list_display = ('pub_date', 'headline', 'author')

site.register(Entry, EntryAdmin)
