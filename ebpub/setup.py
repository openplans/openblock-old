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
with open(os.path.join(here, 'README.txt')) as file:
    long_description = file.read()
    # Add the generic OpenBlock README and the changelog.
    openblock_readme = os.path.join(here, '..', 'README.txt')
    if os.path.exists(openblock_readme):
        with open(openblock_readme) as openblock_readme:
            long_description += '\n\n'
            long_description += openblock_readme.read()
    release_notes = os.path.join(here, '..', 'docs', 'changes', 'release_notes.rst')
    if os.path.exists(release_notes):
        with open(release_notes) as release_notes:
            long_description += '\n\n'
            long_description += release_notes.read()
    # Remove stuff that breaks vanilla rst (no sphinx)
    # and doesn't belong on a pypi page anyway.
    long_description = long_description.split('Older Changes')[0]


VERSION="1.1.0"

setup(
    name='ebpub',
    version=VERSION,
    description="Core models and views for OpenBlock (hyperlocal news for Django)",
    long_description=long_description,
    maintainer="Paul Winkler (for OpenPlans)",
    maintainer_email="ebcode@groups.google.com",
    url="http://openblockproject.org/docs",
    license="GPLv3",
    keywords="openblock",
    install_requires=[
        "django>=1.3.1",
        "django-static",
        "GDAL",
        "pyyaml",
        "psycopg2>=2.0",
        "slimmer",  # used by django-static.
        "pyrfc3339",
        "South",
        "mock>=0.8.0alpha1",
        "django-olwidget",
        'setuptools-git',  # Only needed if building packages for distribution.
        'python-dateutil<2.0',  # 2.0 requires python >= 3.
    ],
    dependency_links=[
    "http://www.voidspace.org.uk/downloads/mock-0.8.0alpha1.tar.gz#egg=mock-0.8.0alpha1",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'send_alerts = ebpub.alerts.sending:main',
            'activate_schema = ebpub.db.bin.activate_schema:main',
            'add_location = ebpub.db.bin.add_location:main',
            'alphabetize_locations = ebpub.db.bin.alphabetize_locations:main',
            'export_schema = ebpub.db.bin.export_schema:main',
            'geocode_newsitems = ebpub.db.bin.geocode_newsitems:main',
            'import_locations = ebpub.db.bin.import_locations:main',
            'import_neighborhoods = ebpub.db.bin.import_hoods:main',
            'import_zips_tiger = ebpub.db.bin.import_zips:main',
            # 'import_zips_esri = ebpub.streets.blockimport.esri.importers.zipcodes:TODO',
            'update_aggregates = ebpub.db.bin.update_aggregates:main',
            'populate_streets = ebpub.streets.bin.populate_streets:main',
            'populate_suburbs = ebpub.streets.bin.populate_suburbs:main',
            'fix_block_numbers = ebpub.streets.bin.fix_block_numbers:main',
            'update_block_pretty_names = ebpub.streets.bin.update_block_pretty_names:update_block_pretty_names',
            'delete_blocks_outside_city = ebpub.streets.bin.delete_blocks_outside_city:delete_blocks_outside_city',
            'import_blocks_tiger = ebpub.streets.blockimport.tiger.import_blocks:main',
            'import_blocks_esri = ebpub.streets.blockimport.esri.importers.blocks:main',
            ],
        },
    classifiers=[
        #'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        ],
)
