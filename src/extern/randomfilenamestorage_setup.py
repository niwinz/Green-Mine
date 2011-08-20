#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='django-randomfilenamestorage',
    version='1.1',
    description=('A Django storage backend that gives random names to files.'),
    long_description=open('README.rst', 'r').read(),
    author='Akoha Inc.',
    author_email='adminmail@akoha.com',
    url='http://bitbucket.org/akoha/django-randomfilenamestorage/',
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
