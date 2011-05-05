#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
import re

class PerModelDBRouter:
    """
    PerModelDBRouteer is a database router as described in the 
    django multi-database documentation: 
    http://docs.djangoproject.com/en/dev/topics/db/multi-db/
    
    The PerModelDBRouter allows you to assign Model types to a 
    particular configured database. 
    
    The django setting DATABASE_ROUTES controls the particulars.
    
    DATABASE_ROUTES is expected to be a dictionary with keys 
    referencing database names in the DATABASES settings and 
    values lists of references to model types of the form 
    <app_label>.<ModelClass> or regular expressions that match
    values of the form.
    
    eg:

    DATABASE_ROUTES = {
        'users': ['accounts.User'],
        'barn': ['animals.Goat', 
                 'animals.Pig'],
        'junkyard': ['garbage.*', 'scrap.*']
    }
    
    This configuration would put accounts.models.User objects into the 
    database 'users', animals.models.Goat and animals.models.Pig into
    the database 'barn' and any model in the garbage or scrap app into 
    the datatbase 'junkyard'
    
    A subclass may optionally provide its own configuration instead of
    using settings.DATABASE_ROUTES, by setting the attribute _routes
    to a dictionary of the same form.
    """
    
    @property
    def routes(self):
        if hasattr(self, '_routes'):
            return self._routes
        else:
            return settings.DATABASE_ROUTES

    def _find_db(self, model):
        for db, routes in self.routes.items():
            for pat in routes: 
                mid = '%s.%s' % (model._meta.app_label, model.__name__)
                if re.match(pat, mid):
                    return db

        return None

    def db_for_read(self, model, **hints):
        return self._find_db(model)

    def db_for_write(self, model, **hints):
        return self._find_db(model)
        
    def allow_relation(self, obj1, obj2, **hints):
        # XXX should validate.
        return None

    def allow_syncdb(self, db, model):
        assigned_db_alias = self._find_db(model)
        # if there is an assigned db, only allow
        # it to be synced to the specific one.
        if assigned_db_alias is None:
            if db in self.routes:
                return False
            else:
                return None
        return assigned_db_alias == db
