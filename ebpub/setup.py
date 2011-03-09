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

setup(
    name='ebpub',
    version="0.1",
    description="",
    license="GPLv3",
    install_requires=[
    "django>=1.2",
    "django-static",
    "GDAL",
    "pyyaml",
    "psycopg2",
    "slimmer",  # used by django-static.
    "pyrfc3339",
    "mock",
    ],
    dependency_links=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points="""
    """,
)
