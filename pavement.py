"""
QnD OpenBlock Installer

TODO:
test basic system expectations (libs etc)
not even pretending unix isn't required
verbosity is rather extreme
network requirement is ugly, cache

demo: 
generate unique values for certain configuration params
"""

import os
import traceback
from paver.easy import *
from paver.setuputils import setup

options(
    # packages to activate 
    # order matters! dependants first
    openblock_packages=[
        'ebgeo',
        'ebpub',
        'ebdata',
        'everyblock'
    ],
    source_dir = '.',

    # paths that will be searched for suitable postgis 
    # add your own if it's custom or not listed.
    postgis_paths = ['/usr/share/postgresql/8.4/contrib',
                     '/usr/share/postgresql-8.3-postgis',
                     '/usr/local/pgsql/share/contrib/postgis-1.5',
                     '/opt/local/share/postgresql84/contrib/postgis-1.5'
    ]
)

@task
def install_aggdraw(options):
    """
    workaround for broken aggdraw on certain
    platforms, may require additional fixes for
    64 bit plaforms, unclear.
    """
    sh('env CFLAGS=-fpermissive bin/pip install aggdraw -E .')

@task
def install_gdal(options):
    """
    workaround for broken GDAL python
    package.
    """

    sh('bin/pip install GDAL\<1.7 --no-install')
    if not os.path.exists('build/GDAL'):
        return

    # has bad settings for gdal-config that 
    # confuse setup.py
    sh('rm build/GDAL/setup.cfg',
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
    
    build = '../../bin/python setup.py build_ext'
    build += ' --gdal-config=gdal-config'
    build += ' --library-dirs=%s' % ':'.join(lib_dirs)
    build += ' --libraries=%s' % ':'.join(libs)
    build += ' --include-dirs=%s' % ':'.join(includes)
    build += ' install'

    sh(build, cwd='build/GDAL')

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
            sh('bin/pip install -r %s' % req_file)

@task
@needs('install_requirements')
def install_ob_packages(options):
    for package_name in options.openblock_packages:
        package_dir = os.path.join(options.source_dir, package_name)
        sh('bin/pip install -e %s -E.' % package_dir)

@task
@needs('install_ob_packages')
def post_bootstrap(options):
    print "Success! OpenBlock packages installed."


@task
def install_demo(options):
    """
    sets up the obdemo package.
    """
    sh('bin/pip install -e obdemo -E.')

    # create openblock settings if none have been created
    real_settings = os.path.join('obdemo', 'obdemo', 'real_settings.py')
    default_settings = os.path.join('obdemo', 'obdemo', 'real_settings.py.in')
    
    if not os.path.exists(real_settings):
        print "Setting up with default settings => %s" % real_settings
        sh('cp %s %s' % (default_settings, real_settings))

    print "\nThe obdemo package is now installed."
    print "Please review the settings in %s." % real_settings

@task
def create_demo_db(options):
    import obdemo.settings
    create_databases(options, obdemo.settings)

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

def create_databases(options, settings):
    """
    create databases referenced in django settings.
    """

    # find postgis before we get into messing around with 
    # other stuff too deeply.
    postgis_files = find_postgis(options)
    if not postgis_files: 
        print "Cannot locate postgis sql!"
        sys.exit(1)

    import psycopg2

    # just supports 'the one' database for now
     
    dbhost = settings.DATABASE_HOST
    dbport = settings.DATABASE_PORT
    dbname = settings.DATABASE_NAME
    dbuser = settings.DATABASE_USER
    dbpass = settings.DATABASE_PASSWORD

    dbcfg = {}
    if dbhost:
        dbcfg['host'] = dbhost
    if dbport:
        dbcfg['port'] = dbport

    #####################################
    #
    # check connection
    #
    #####################################

    # try to connect to the postgres database
    try:
        conn = psycopg2.connect(database="postgres", **dbcfg)
        print "Connected to postgres"
    except psycopg2.OperationalError:
        # settings or current user are wrong ?
        traceback.print_exc()
        print "Couldn't connect to postgres."
        sys.exit(1)

    ################################
    #
    # create user
    #
    ################################

    # test if the user exists
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pg_roles WHERE rolname='%s';" % dbuser)
    if cur.fetchone()[0] == 0:
        try:
            print "Creating user '%s'..." % dbuser
            cur.execute("CREATE ROLE %s PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN;" % 
                        (dbuser, dbpass))
            conn.commit()
        except:
            traceback.print_exc()
            print "Failed to create user."
            sys.exit(1)
    else:
        print "User '%s' already exists, leaving it alone..." % dbuser

    ##################################
    #
    # create database
    #
    ##################################

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    # check if the openblock database already exists
    cur.execute("SELECT COUNT(*) from pg_database where datname='%s';" %
                dbname)
    if cur.fetchone()[0] != 0:
        print "Database %s already exists, leaving it alone..." % dbname
        return

    print "Creating database %s'" % dbname
    try:
        cur.execute("CREATE DATABASE %s OWNER %s;" % (dbname, dbuser))
    except:
        traceback.print_exc()
        print "Failed to create database."
        sys.exit(1)

    # cool, reconnect to our new database.
    print "reconnecting to database %s" % dbname 
    conn = psycopg2.connect(database=dbname, **dbcfg)
    cur = conn.cursor()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    #################################
    #
    # create plpgsql language
    #
    #################################
    cur.execute("SELECT COUNT(*) from pg_language where lanname='plpgsql';")
    if cur.fetchone()[0] == 0:
        print "creating language plpgsql..."
        cur.execute("CREATE LANGUAGE plpgsql;")
    else:
        print "language plpgsql already exists, moving on..."
    conn.close()

    ###################################
    # 
    # load postgis sql
    #
    ###################################
    print "Loading postgis from %s" % ', '.join(postgis_files)
    for filename in postgis_files: 
        sh("psql -d %s -f %s" % (dbname, filename))

    # make the postgis tables accessable to openblock user
    print "granting rights on postgis tables to %s" % dbuser
    conn = psycopg2.connect(database=dbname, **dbcfg)
    cur = conn.cursor()
    cur.execute("GRANT ALL ON TABLE geometry_columns TO %s;" % dbuser)
    cur.execute("GRANT ALL ON TABLE spatial_ref_sys TO %s;" % dbuser)
    conn.commit()
    conn.close()

    print "Success. database %s created." % dbname


