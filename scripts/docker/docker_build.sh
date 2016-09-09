#!/bin/bash
BUILE_LOG=build.log
IMAGE_BASE_NAME=$1
VERSION=`grep 'version:' ../rpm/build_rpm.yml |sed 's/version: //g'`
RELEASE=`grep 'release:' ../rpm/build_rpm.yml |sed 's/release: //g'`

FINALE_VERSION=${VERSION}'-'${RELEASE}

echo ' -------------------start import letv-centos6 images----------------------' > ${BUILE_LOG}
docker import http://pkg-repo.oss.letv.com/pkgs/centos6/images/letv-centos6.tar letv:centos6 >> ${BUILE_LOG}
echo ' -------------------finish import letv-centos6 images----------------------' >> ${BUILE_LOG}

echo ' -------------------start building elasticsearch images----------------------' >> ${BUILE_LOG}
docker build -t="${IMAGE_BASE_NAME}:${FINALE_VERSION}" . >> ${BUILE_LOG}
echo ' -------------------finish building elasticsearch images----------------------' >> ${BUILE_LOG}
