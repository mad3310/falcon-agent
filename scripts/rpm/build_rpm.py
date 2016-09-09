#!/usr/bin/env python2.6
# encoding: utf-8

import os

from fabric.api import local, lcd
from fabric.colors import yellow, green
import yaml

PROJECT_ROOT = os.path.split(os.path.realpath(__file__))[0]
PACKOUT = os.path.join(PROJECT_ROOT, 'rpms')

def generate_rpm():
    print(yellow("Start generate rpm package ..."))
    commad = """fpm -f \
        -s {source_type} \
        -t {target_type} \
        -C {buildroot} \
        -n {name} \
        -v {version} \
        -m "{maintainor}" \
        -p {packout} \
        --category "{category}" \
        --description "{description}" \
        --url "{url}" \
        --vendor "{vendor}" \
        --before-install {before_install} \
        --after-install {after_install} \
        --after-remove {after_remove} \
        --iteration {release} \
        --verbose""".format(
        source_type=y['source_type'],
        target_type=y['target_type'],
        buildroot=os.path.join(project_root, 'build'),
        name=y['name'],
        version=y['version'],
        maintainor=y['maintainor'],
        packout=PACKOUT,
        category=y['category'],
        description=y['description'],
        url=y['url'],
        vendor=y['vendor'],
        before_install=os.path.join(project_root, y['before_install']),
        after_install=os.path.join(project_root, y['after_install']),
        after_remove=os.path.join(project_root, y['after_remove']),
        release=y['release']
    )
    local(commad)
    print(green("Generate rpm package Successful!"))


def upload_rpm():
    pass


def clean():
    local("rm -rf {0}".format(project_root))


if __name__ == "__main__":
    y = yaml.safe_load(open('build_rpm.yml'))
    project_root = PROJECT_ROOT
    #clean()
    #download_source()
    #build_source()
    generate_rpm()
    #clean()
