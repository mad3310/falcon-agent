#!/bin/bash
PACKAGE_NAME=monitor_center
RPM_NAME=monitor-center
pip uninstall -y ${PACKAGE_NAME}
rm -rf /opt/letv/${RPM_NAME}
rm -rf /etc/init.d/${RPM_NAME}
rm -rf /etc/sysconfig/${RPM_NAME}

exit 0
