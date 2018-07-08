# coding: utf-8

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_txt = f.read()

setup(
    name='wsrequests',
    version='0.1.1',
    description='thin wrapper for requests enable websocket',
    long_description=readme,
    author='denzow',
    author_email='denzow@gmail.com',
    url='https://github.com/denzow/wsrequests',
    license=license_txt,
    packages=find_packages(exclude=('examples',)),
    install_requires=[
        'requests',
        'websocket-client',
    ],
)
