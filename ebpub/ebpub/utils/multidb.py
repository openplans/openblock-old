from django.conf import settings

class PerModelDBRouter:
    """
    PerModelDBRouteer is a database router as described in the 
    django multi-database documentation: 
    http://docs.djangoproject.com/en/dev/topics/db/multi-db/
    
    The PerModelDBRouter allows you to assign the exact list of 
    Model types assigned to a particular configured databases.  
    The django setting DATABASE_ROUTES controls the particulars.
    
    DATABASE_ROUTES is expected to be a dictionary with keys 
    referencing database names in the DATABASES settings and 
    values lists of references to model types of the form 
    (app_label, ModelClass).
    
    eg:

    DATABASE_ROUTES = {
        'users': [('accounts', 'User')],
        'barn': [('animals', 'Goat'), 
                 ('animals', 'Pig')]
    }
    
    This configuration would put accounts.models.User objects into the 
    database 'users' and animals.models.Goat and animals.models.Pig into
    the database 'barn'
    
    A subclass may optionally provide a specific configuration value to 
    the attribute _routes (of the same form) to override the use of
    detailed settings.
    """
    
    @property
    def routes(self):
        if hasattr(self, '_routes'):
            return self._routes
        else:
            return settings.DATABASE_ROUTES

    def _find_db(self, model):
        for db, routes in self.routes.items():
            for app_label, name in routes: 
                if (model._meta.app_label == app_label and
                    model.__name__ == name):
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
        rdb = self._find_db(model)
        if rdb is None:
            if db in self.routes:
                return False
            else:
                return None
        return rdb == db