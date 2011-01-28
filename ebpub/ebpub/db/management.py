
from django.db.models.signals import final_post_syncdb
import ebpub.db.models
import os
import sys

def location_post_syncdb_callback(sender, **kwargs):
    """
    Do final database setup that can only be done after syncdb fully
    finishes, eg. things that rely on Geometry fields (which aren't
    created until the `sqlindexes` phase, *after* `sqlcustom`).

    Depends on a 'final_post_syncdb' signal, which does not
    exist in stock Django 1.2.
    So we added it, see monkeypatches.py,
    and see http://code.djangoproject.com/ticket/7561
    """
    # This gets called for all models modules; check we got the right one.
    if sender.__name__ != 'ebpub.db.models':
        return
    # Make sure to use the right database connection.
    db = kwargs['db']
    if db != sender.Location.objects.db:
        return
    from django.db import connections
    cursor = connections[db].cursor()

    # Load relevant post-syncdb sql files.
    sql_dir = os.path.normpath(os.path.join(os.path.dirname(ebpub.db.models.__file__), 'sql'))
    sql_file = os.path.join(sql_dir, "location_post_syncdb.sql")
    try:
        if os.path.exists(sql_file):
            print "Loading extra post-syncdb SQL data from '%s'" % sql_file
            f = open(sql_file)
            sql = f.read()
            f.close()
            cursor.execute(sql)
    except Exception, e:
        sys.stderr.write("Failed to install post-syncdb SQL file '%s': %s\n" % \
                             (sql_file, e))
        import traceback
        traceback.print_exc()

final_post_syncdb.connect(location_post_syncdb_callback)
