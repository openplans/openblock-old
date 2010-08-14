"""
QnD OpenBlock Installer

TODO:
test basic system expectations (libs etc)
not even pretending unix isn't required
verbosity is rather extreme
network requirement is ugly, cache
"""

import os
from paver.easy import *
from paver.setuputils import setup

options(
    # packages to activate 
    # order matters! dependants first
    openblock_packages=[
        'ebgeo',
        'ebpub',
        'ebdata'
    ],
    source_dir = '.',
)

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
@needs('install_gdal')
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
        sh('bin/pip install -e %s' % package_dir)

@task
@needs('install_ob_packages')
def post_bootstrap(options):
    print "Great Success!"
