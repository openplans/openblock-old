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

# Sanity-check python version.
import sys
if not ((2, 6) <= sys.version_info[:2] < (3, 0)):
    sys.exit("ERROR: ebpub requires Python >= 2.6 and < 3.0")

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import os.path
here = os.path.dirname(__file__)
with open(os.path.join(here, 'README.TXT')) as file:
    long_description = file.read()

setup(
    name='ebpub',
    version="1.0a2-dev",
    description="Core models and views for OpenBlock (Hyperlocal news Django app)",
    long_description=long_description,
    license="GPLv3",
    install_requires=[
    "django>=1.3",
    "django-static",
    "GDAL",
    "pyyaml",
    "psycopg2>=2.0",
    "slimmer",  # used by django-static.
    "pyrfc3339",
    "South",
    "mock>=0.8.0alpha1",
    'setuptools-git',  # Only needed if building packages for distribution.
    'django-apikey',
    ],
    find_links=[
    ],
    dependency_links=[
    "http://www.voidspace.org.uk/downloads/mock-0.8.0alpha1.tar.gz#egg=mock-0.8.0alpha1",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points="""
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        ],
)
