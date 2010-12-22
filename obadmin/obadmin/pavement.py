"""
Quick and Dirty OpenBlock Installer

TODO:
test basic system expectations (libs etc)
not even pretending unix isn't required
verbosity is rather extreme
network requirement is ugly, cache
generate unique values for certain configuration params (cookies etc)
bad existing postgis_template can interfere with install, test
"""

import glob
import os
import traceback

from paver.easy import *

options(
    # packages to activate
    # order matters! dependants first
    openblock_packages=[
        'ebpub',
        'ebdata',
        'obadmin',
        'everyblock',
    ],

    # assumes pavement.py is in source_dir/obadmin/obadmin/pavement.py
    source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))),

    app='obdemo',
    # paths that will be searched for suitable postgis
    # add your own if it's custom or not listed.
    # These will be treated as patterns for glob.glob()
    postgis_paths = ['/usr/share/postgresql/8.*/contrib',
                     '/usr/share/postgresql-8.*-postgis',
                     '/usr/local/pgsql/share/contrib/postgis-1.*',
                     '/opt/local/share/postgresql84/contrib/postgis-1.*',
                     '/usr/local/Cellar/postgis/1.*/share/postgis',
    ],
    default_postgis_template='template_postgis'
)

@task
def auto(options):
    # determine the root of the virtual env
    options.env_root = os.path.abspath(os.environ.get('VIRTUAL_ENV', '.'))
    # XXX better test.
    if not os.path.exists(os.path.join(options.env_root, 'bin', 'paver')):
        print "It does not appear that your virutal environment is activated or that you are in its root."
        print "please activate your environment and try again."
        sys.exit(0)
    print "Using virtual env %s" % options.env_root

@task
def install_aggdraw(options):
    """
    workaround for broken aggdraw on certain
    platforms, may require additional fixes for
    64 bit plaforms, unclear.
    """
    os.chdir(options.env_root)
    sh('env CFLAGS=-fpermissive %s/bin/pip install aggdraw' % options.env_root)


@task
@needs('install_aggdraw')
def install_ebgeo(options):
    # XXX TODO install mapnik
    package_dir = os.path.join(options.source_dir, 'ebgeo')
    sh('%s/bin/pip install -e %s' % (options.env_root, package_dir))
    print "Installed ebgeo.  Adjust your django settings to include this app."

@task
def install_gdal(options):
    """
    workaround for broken GDAL python
    package, if we need to install it.
    """
    try:
        import gdal
        return
    except:
        pass
    libgdal_version = sh('gdal-config --version', capture=True)
    gdal_req = libgdal_version.split('.')
    gdal_req = '.'.join([gdal_req[0], str(int(gdal_req[1]) + 1)])

    print "Looks like you have libgdal version %s" % libgdal_version
    print "trying to get python package version <%s" % gdal_req

    sh('%s/bin/pip install GDAL\<%s --no-install' % (options.env_root, gdal_req))
    if not os.path.exists('%s/build/GDAL' % options.env_root):
        return

    # has bad settings for gdal-config that
    # confuse setup.py
    sh('rm %s/build/GDAL/setup.cfg' % options.env_root,
       ignore_error=True)

    # also, library and include dirs are just
    # guesses from the prefix setting
    # so we dig them out of the config.

    includes = [x[2:] for x in
                sh('gdal-config --cflags', capture=True).split()
                if x.startswith('-I')]
    lib_config = sh('gdal-config --libs', capture=True)
    lib_dirs = [x[2:] for x in
            lib_config.split()
            if x.startswith('-L')]
    libs = [x[2:] for x in
            lib_config.split()
            if x.startswith('-l')]

    build = '%s/bin/python setup.py build_ext' % options.env_root
    build += ' --gdal-config=gdal-config'
    build += ' --library-dirs=%s' % ':'.join(lib_dirs)
    build += ' --libraries=%s' % ':'.join(libs)
    build += ' --include-dirs=%s' % ':'.join(includes)
    build += ' install'

    sh(build, cwd='%s/build/GDAL' % options.env_root)

@task
@needs('install_gdal')
def install_requirements(options):
    """
    install dependancies listed in the
    requirements.txt files in each package.
    """
    for package_name in options.openblock_packages:
        print "gathering dependencies for %s" % package_name
        req_file = os.path.join(options.source_dir, 
                                package_name, 
                                'requirements.txt')
        if os.path.exists(req_file):
            sh('%s/bin/pip install -r %s' % (options.env_root, req_file))

@task
@needs('install_requirements')
def apply_patches(options):
    # For anything installed with pip -e, we can apply patches
    # by dropping them in the patches/ directory.
    patch_dir = os.path.join(options.source_dir, 'patches')
    source_dir = os.path.join(options.env_root, 'src')
    assert os.path.exists(patch_dir)
    assert os.path.exists(source_dir)
    for patchfile in glob.glob(os.path.join(patch_dir, '*patch')):
        # Force-applying a patch more than once can be dangerous,
        # so we do a dry run first and check for problems.
        patchfile = os.path.abspath(patchfile)
        args = '-f -p1 -i %s' % patchfile
        try:
            print "Testing patch %s..." % patchfile
            sh('patch --dry-run %s' % args, cwd=source_dir,
               capture=True)
        except BuildFailure:
            print "Skipping, see errors above"
        else:
            print "OK, applying patch %s" % patchfile
            sh('patch %s' % args, cwd=source_dir)
        print "-" * 60

@task
@needs('apply_patches')
def install_ob_packages(options):
    for package_name in options.openblock_packages:
        package_dir = os.path.join(options.source_dir, package_name)
        sh('%s/bin/pip install -e %s' % (options.env_root, package_dir))
    print "Success! OpenBlock packages installed."

@task
@needs('install_ob_packages')
def install_manage_script(options):
    """
    creates a manage.py script in $VIRTUALENV so you don't have to
    specify a settings module.
    """
    source = os.path.join(options.source_dir, options.app, options.app, 'manage.sh')
    dest = os.path.join(options.env_root, 'manage.py')
    if not os.path.exists(dest):
        os.symlink(source, dest)

@task
@needs('install_ob_packages', 'install_manage_script')
def install_app(options):
    """
    sets up django app options.app
    """
    app_dir = os.path.join(options.source_dir, options.app)
    sh('%s/bin/pip install -e %s' % (options.env_root, app_dir))

    # create openblock settings if none have been created
    local_settings = os.path.join(options.source_dir, options.app, options.app,
                                  'settings.py')
    settings_skel = local_settings + '.in'

    if not os.path.exists(local_settings):
        print "Creating settings settings file => %s" % local_settings
        s = open(settings_skel).read()
        # Replace default salts with random strings.
        need_replacing = '<REPLACE_ME>'
        while s.count(need_replacing):
            s = s.replace(need_replacing, _random_string(), 1)
        open(local_settings, 'w').write(s)


    print "\nThe %s package is now installed." % options.app
    print "Please review the settings in %s." % local_settings



@task
@needs('install_app')
def post_bootstrap(options):
    # we expect this task is run automatically by our bootstrap.py script.
    print "Once you like your settings, run 'sudo -u postgres bin/oblock app=%s setup_dbs'" % options.app

def find_postgis(options):
    file_sets = (
        ('postgis.sql', 'spatial_ref_sys.sql'),
        ('lwpostgis.sql', 'spatial_ref_sys.sql')
    )
    postgis_paths = []
    for pattern in options.postgis_paths:
        postgis_paths.extend(glob.glob(pattern))
    for path in postgis_paths:
        for files in file_sets:
            found = True
            for filename in files:
                check_file = os.path.join(path, filename)
                if not os.path.exists(check_file):
                    found = False
                    break
            if found == True:
                return [os.path.join(path, filename) for filename in files]
    return None


def get_app_settings(options):
    settings_module = '%s.settings_default' % options.app
    user_settings_module = '%s.settings' % options.app
    try:
        __import__(user_settings_module)
    except:
        exit_with_traceback("Problem with %s or %s, see above"
                            % (settings_module, user_settings_module))
    return sys.modules[user_settings_module]

def get_conn_params(dbinfo):
    dbhost = dbinfo.get('HOST', None)
    dbport = dbinfo.get('PORT', None)

    params = {}
    if dbhost:
        params['host'] = dbhost
    if dbport:
        params['port'] = dbport
    return params

def _distinct_servers(settings):
    dbs = {}
    for dbname, dbinfo in settings.DATABASES.items():
        dbid = (dbinfo.get('HOST'), dbinfo.get('PORT'))
        dbs[dbid] = dbinfo
    return dbs.values()

def _distinct_dbs(settings):
    dbs = {}
    for dbname, dbinfo in settings.DATABASES.items():
        dbid = (dbinfo.get('HOST'), dbinfo.get('PORT'), dbinfo.get('NAME'))
        dbs[dbid] = dbinfo
    return dbs.values()

def _distinct_users(settings):
    dbs = {}
    for dbname, dbinfo in settings.DATABASES.items():
        dbid = (dbinfo.get('HOST'), dbinfo.get('PORT'), dbinfo.get('USERNAME'))
        dbs[dbid] = dbinfo
    return dbs.values()

@task
def sync_all(options):
    """Use django-admin to initialize all our databases.
    """
    settings_mod = "%s.settings" % options.app
    settings = get_app_settings(options)
    for dbname in settings.DATABASE_SYNC_ORDER:
        sh("django-admin.py syncdb --settings=%s --database=%s --noinput" % (settings_mod, dbname))

    for dbname in settings.DATABASES.keys():
        if dbname not in settings.DATABASE_SYNC_ORDER:
            sh("django-admin.py syncdb --settings=%s --database=%s --noinput" % (settings_mod, dbname))
    # Need workaround here for
    # http://developer.openblockproject.org/ticket/74 because geometry
    # columns don't exist yet at the time that Django loads an app's
    # custom sql.  We can't just re-run all the custom sql because Django
    # wraps it in a transaction, and some of it has already run and can't
    # re-run without errors. So, just run the stuff we need.
    # XXX verify this works with stdin redirect? and what's the cwd?
    # FIXME: how to know which database to use?
    sh("django-admin.py dbshell --settings=%s < ../../ebpub/ebpub/db/sql/location.sql" % settings_mod)


@task
@needs('create_database_users')
@needs('create_postgis_templates')
def setup_dbs(options):
    """
    create application database(s).
    """
    settings = get_app_settings(options)
    for dbinfo in _distinct_dbs(settings):
        _setup_db(options, settings, dbinfo)
    print "Success! Now run 'oblock app=%s sync_all'" % options.app

def _setup_db(options, settings, dbinfo):
    conn_params = get_conn_params(dbinfo)

    import psycopg2
    conn = psycopg2.connect(database="postgres", **conn_params)

    dbuser = dbinfo.get('USER')

    cur = conn.cursor()
    dbname = dbinfo.get('NAME')
    template = settings.POSTGIS_TEMPLATE
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                dbname)
    if cur.fetchone()[0] != 0:
        print "Database '%s' already exists, fixing permissions ..." % dbname
        grant_rights_on_spatial_tables(dbname, **conn_params)
        return

    print "Creating database %s'" % dbname
    try:
        cur.execute("CREATE DATABASE %s OWNER %s TEMPLATE %s;" % (dbname, dbuser, template))
    except:
        exit_with_traceback("Failed to create database %r" % dbname)

    grant_rights_on_spatial_tables(dbname, **conn_params)
    print "Success. created database %s owned by %s" % (dbname, dbuser)

@task
def create_database_users(options):
    settings = get_app_settings(options)
    for dbinfo in _distinct_users(settings):
        _create_database_user(options, settings, dbinfo)

def _create_database_user(options, settings, dbinfo):
    conn_params = get_conn_params(dbinfo)

    import psycopg2
    conn = psycopg2.connect(database="postgres", **conn_params)

    ################################
    #
    # create user
    #
    ################################
    dbuser = dbinfo.get('USER')
    dbpass = dbinfo.get('PASSWORD')

    cur = conn.cursor()
    # test if the user exists
    cur.execute("SELECT COUNT(*) FROM pg_roles WHERE rolname='%s';" % dbuser)
    if cur.fetchone()[0] == 0:
        try:
            print "Creating user '%s'..." % dbuser
            cur.execute("CREATE ROLE %s PASSWORD '%s' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;" %
                        (dbuser, dbpass))
            conn.commit()
        except:
            exit_with_traceback("Failed to create user.")
    else:
        print "User '%s' already exists, leaving it alone..." % dbuser

@task
def drop_dbs(options):
    """
    drop application database(s).
    """
    settings = get_app_settings(options)
    for dbinfo in _distinct_dbs(settings):
        dbname = dbinfo.get('NAME')
        _drop_postgis_db(dbname, settings, dbinfo)

def _drop_postgis_db(dbname, settings, dbinfo, is_template=False):
    conn_params = get_conn_params(dbinfo)
    import psycopg2
    conn = psycopg2.connect(database="postgres", **conn_params)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                dbname)
    if cur.fetchone()[0] == 0:
        print "database %s does not exist." % dbname
        return

    if is_template:
        # set it to a non-template so it can be dropped
        cur.execute("UPDATE pg_database SET datistemplate = FALSE "
                    "where datname='%s';" % dbname)
    # drop it
    cur.execute("DROP DATABASE %s;" % dbname)
    print "Dropped database %s" % dbname

@task
def drop_postgis_templates(options):
    settings = get_app_settings(options)
    for dbinfo in _distinct_servers(settings):
        _drop_postgis_template(settings, dbinfo)


def _drop_postgis_template(settings, dbinfo):
    name = settings.POSTGIS_TEMPLATE
    return _drop_postgis_db(name, settings, dbinfo, is_template=True)


@task
def create_postgis_templates(options):
    settings = get_app_settings(options)
    for dbinfo in _distinct_servers(settings):
        _create_postgis_template(options, settings, dbinfo)

def _create_postgis_template(options, settings, dbinfo):
    conn_params = get_conn_params(dbinfo)
    import psycopg2
    conn = psycopg2.connect(database="postgres", **conn_params)

    ##################################
    #
    # create template
    #
    ##################################

    template = settings.POSTGIS_TEMPLATE
    make_template_sql = "UPDATE pg_database set datistemplate = true where datname='%s';" % template

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    # check if the database already exists
    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                template)
    if cur.fetchone()[0] != 0:
        print "Database '%s' already exists, fixing permissions..." % template
        grant_rights_on_spatial_tables(template, **conn_params)
        cur.execute(make_template_sql)
        return

    postgis_files = find_postgis(options)
    if not postgis_files:
        print "Cannot locate postgis sql.  Please verify that PostGIS is installed."
        sys.exit(1)

    print "Creating template %s'" % template
    try:
        cur.execute("CREATE DATABASE %s ENCODING 'UTF8';" % template)
        cur.execute(make_template_sql)
    except:
        exit_with_traceback("Failed to create template %r" % template)

    # cool, reconnect to our new database.
    print "reconnecting to database %s" % template
    conn = psycopg2.connect(database=template, **conn_params)
    cur = conn.cursor()

    #################################
    #
    # create plpgsql language
    #
    #################################
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute("SELECT COUNT(*) from pg_language where lanname='plpgsql';")
    if cur.fetchone()[0] == 0:
        print "creating language plpgsql..."
        cur.execute("CREATE LANGUAGE plpgsql;")
    else:
        print "Language 'plpgsql' already exists.  moving on..."
    conn.close()

    ###################################
    #
    # load postgis sql
    #
    ###################################
    print "Loading postgis from %s" % ', '.join(postgis_files)
    for filename in postgis_files:
        sh("psql -d %s -f %s" % (template, filename))

    print "created postgis template %s." % template
    grant_rights_on_spatial_tables(template, **conn_params)


def grant_rights_on_spatial_tables(database, **conn_params):
    import psycopg2
    conn = psycopg2.connect(database=database, **conn_params)
    cur = conn.cursor()
    cur.execute("GRANT ALL ON TABLE geometry_columns TO PUBLIC;")
    cur.execute("GRANT ALL ON TABLE spatial_ref_sys TO PUBLIC;")
    conn.commit()
    print "granting rights on postgis tables to public"


def exit_with_traceback(extra_msg):
    traceback.print_exc()
    print "=============================================="
    print extra_msg
    sys.exit(1)

def _random_string(length=12):
    import random
    import string
    result = ''
    for i in range(length):
        result += random.choice(string.letters + string.digits)
    return result

def main():
    import os
    import sys
    from paver.tasks import main as paver_main
    args = ['-f',  os.path.join(os.path.dirname(__file__), 'pavement.py')]
    args = args + sys.argv[1:]
    paver_main(args)

if __name__ == '__main__':
    main()
