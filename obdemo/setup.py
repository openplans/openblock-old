try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='obdemo',
    version="0.1",
    description="",
    license="GPLv3",
    install_requires=[
    "ebgeo",
    "ebpub",
    "ebdata",
    "geopy", # Maybe. Alternative to ebpub's geocoder.
    ],
    dependency_links=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points="""
    """,
)
