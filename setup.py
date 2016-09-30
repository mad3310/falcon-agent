#coding=utf-8

#from distutils.core import setup
from setuptools import setup
setup(
    name = 'monitor_center',
    version = '0.0.1',
    packages = ['monitor_center'],
    author = 'letv gcp',
    author_email = 'liujinliu@le.com',
    description = 'monitor center',
    entry_points = {
        'console_scripts':[
            'monitor-center-start=monitor_center.main:main'
            ]
        }
    )
