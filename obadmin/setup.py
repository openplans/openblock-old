#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

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

VERSION="1.0a2-dev"

setup(
    name='obadmin',
    version=VERSION,
    description="Setup and administrative tools for ebpub",
    long_description=long_description,
    license="GPLv3",
    install_requires=[
        # Assume openblock packages are versioned together.
        "ebpub>=%s" % VERSION,
        "ebdata>=%s" % VERSION,
        "PasteScript",
        "paver",
    ],
    dependency_links=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points="""
    [console_scripts]
    oblock = obadmin.pavement:main
    
    [paste.paster_create_template]
    openblock = obadmin.skel:OpenblockTemplate
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
