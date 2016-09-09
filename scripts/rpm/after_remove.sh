#!/bin/bash

pip uninstall -y falcon_agent
rm -rf /opt/letv/falcon-agent
rm -rf /etc/init.d/falcon-agent
rm -rf /etc/sysconfig/falcon-agent

exit 0
