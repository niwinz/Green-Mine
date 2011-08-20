#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='django-dbstorage',
    version='1.3',
    description=('A Django file storage backend for files in the database.'),
    long_description=open('README.rst', 'r').read(),
    author='Akoha Inc.',
    author_email='adminmail@akoha.com',
    url='http://bitbucket.org/akoha/django-dbstorage/',
    packages=find_packages(),
    install_requires=['Django>=1.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=True,
)
