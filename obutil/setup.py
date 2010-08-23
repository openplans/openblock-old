try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='obutil',
    version="0.1",
    description="",
    license="GPLv3",
    install_requires=[
    ],
    dependency_links=[
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    obenv = obutil.pavement:main
    """,
)