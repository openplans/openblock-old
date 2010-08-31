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

import os
import traceback

from paver.easy import *
from paver.setuputils import setup

options(
    # packages to activate 
    # order matters! dependants first
    openblock_packages=[
        'obutil',
        'ebgeo',
        'ebpub',
        'ebdata',
        'everyblock'
    ],

    # assumes pavement.py is in source_dir/obutil/obutil/pavement.py
    source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))),

    app='obdemo',
    user_settings='real_settings',
    # paths that will be searched for suitable postgis 
    # add your own if it's custom or not listed.
    postgis_paths = ['/usr/share/postgresql/8.4/contrib',
                     '/usr/share/postgresql-8.3-postgis',
                     '/usr/local/pgsql/share/contrib/postgis-1.5',
                     '/opt/local/share/postgresql84/contrib/postgis-1.5'
    ],
    default_postgis_template='template_postgis'
)

@task
def auto(options):
    # determine the root of the virutal env
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
def install_gdal(options):
    """
    workaround for broken GDAL python
    package.
    """

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
@needs('install_gdal', 'install_aggdraw')
def install_requirements(options):
    """
    install dependancies listed in the
    requirements.txt files in each package.
    """
    for package_name in options.openblock_packages:
        print "gathing dependancies for %s" % package_name
        req_file = os.path.join(options.source_dir, 
                                package_name, 
                                'requirements.txt')
        if os.path.exists(req_file):
            sh('%s/bin/pip install -r %s' % (options.env_root, req_file))

@task
@needs('install_requirements')
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
    real_settings = os.path.join(options.source_dir, options.app, options.app,
                                 options.user_settings + '.py')
    default_settings = real_settings + '.in'
    
    if not os.path.exists(real_settings):
        print "Setting up with default settings => %s" % real_settings
        sh('cp %s %s' % (default_settings, real_settings))

    print "\nThe %s package is now installed." % options.app
    print "Please review the settings in %s." % real_settings



@task
@needs('install_app')
def post_bootstrap(options):
    # we expect this task is run automatically by our bootstrap.py script.
    print "Once you like your settings, run 'sudo -u postgres bin/oblock setup_db'"

def find_postgis(options): 
    file_sets = (
        ('postgis.sql', 'spatial_ref_sys.sql'),
        ('lwpostgis.sql', 'spatial_ref_sys.sql')
    )
    for path in options.postgis_paths:
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
    settings_module = '%s.settings' % options.app
    user_settings_module = '%s.%s' % (options.app, options.user_settings)
    try:
        __import__(settings_module)
    except:
        exit_with_traceback("Problem with %s or %s, see above"
                            % (settings_module, user_settings_module))
    return sys.modules[settings_module] 

def get_db_cfg(settings):
    dbhost = settings.DATABASE_HOST
    dbport = settings.DATABASE_PORT

    dbcfg = {}
    if dbhost:
        dbcfg['host'] = dbhost
    if dbport:
        dbcfg['port'] = dbport
    return dbcfg

@task
@needs('create_postgis_template')
def setup_db(options):
    """
    create application database.
    """
    _setup_db(options)
    print "Success! Now run './manage.py syncdb'"

def _setup_db(options):
    settings = get_app_settings(options)
    dbcfg = get_db_cfg(settings)
    import psycopg2
    conn = psycopg2.connect(database="postgres", **dbcfg)

    ################################
    #
    # create app user
    #
    ################################
    dbuser = settings.DATABASE_USER
    dbpass = settings.DATABASE_PASSWORD

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

    ################################
    #
    # create app database
    #
    ################################
    dbname = settings.DATABASE_NAME
    template = settings.POSTGIS_TEMPLATE
    import psycopg2
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                dbname)
    if cur.fetchone()[0] != 0:
        print "Database '%s' already exists, fixing permissions ..." % dbname
        grant_rights_on_spatial_tables(dbname, **dbcfg)
        return

    print "Creating database %s'" % dbname
    try:
        cur.execute("CREATE DATABASE %s OWNER %s TEMPLATE %s;" % (dbname, dbuser, template))
    except:
        exit_with_traceback("Failed to create database %r" % dbname)

    grant_rights_on_spatial_tables(dbname, **dbcfg)
    print "Success. created database %s owned by %s" % (dbname, dbuser)
    
@task
def drop_postgis_template(options):
    settings = get_app_settings(options)
    dbcfg = get_db_cfg(settings)
    import psycopg2
    conn = psycopg2.connect(database="postgres", **dbcfg)
    template = settings.POSTGIS_TEMPLATE

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                template)
    if cur.fetchone()[0] == 0:
        print "template %s does not exist." % template
        return

    # set it to a non-template so it can be dropped
    cur.execute("UPDATE pg_database SET datistemplate = FALSE where datname='%s';" %
                template)
    # drop it
    cur.execute("DROP DATABASE %s;" % template)
    
    print "Dropped database %s" % template 


@task
def create_postgis_template(options):

    settings = get_app_settings(options)
    dbcfg = get_db_cfg(settings)
    import psycopg2
    conn = psycopg2.connect(database="postgres", **dbcfg)

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
        grant_rights_on_spatial_tables(template, **dbcfg)
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
    conn = psycopg2.connect(database=template, **dbcfg)
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


def grant_rights_on_spatial_tables(database, **dbcfg):    
    import psycopg2
    conn = psycopg2.connect(database=database, **dbcfg)
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


def main():
    import os
    import sys
    from paver.tasks import main as paver_main
    args = ['-f',  os.path.join(os.path.dirname(__file__), 'pavement.py')]
    args = args + sys.argv[1:]
    paver_main(args)

if __name__ == '__main__':
    main()


