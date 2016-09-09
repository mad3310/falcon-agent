#coding=utf-8

#from distutils.core import setup
from setuptools import setup
setup(
    name = 'falcon_agent',
    version = '0.0.1',
    packages = ['falcon_agent'],
    author = 'letv gcp',
    author_email = 'liujinliu@le.com',
    description = 'falcon agent',
    entry_points = {
        'console_scripts':[
            'falcon-agent-start=falcon_agent.main:main'
            ]
        }
    )
