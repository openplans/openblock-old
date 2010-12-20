try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='obadmin',
    version="0.1",
    description="",
    license="GPLv3",
    install_requires=[
    "ebpub",
    "ebdata",
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
)
