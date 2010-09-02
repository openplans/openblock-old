try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='ebdata',
    version="0.1",
    description="",
    license="GPLv3",
    install_requires=[
    "django",
    "ebgeo",
    "ebpub",
    "lxml",
    "chardet==1.0.1",
    "feedparser==4.1",
    "httplib2==0.6.0",
    "python-dateutil==1.4.1",
    "xlrd==0.7.1"    
    ],
    dependency_links=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points="""
    """,
)
