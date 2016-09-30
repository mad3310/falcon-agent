#!/bin/bash

#VIRTUAL_ENV_ROOT=virtualenvs
#VENV_NAME=falcon_agent_py26

#source /opt/${VIRTUAL_ENV_ROOT}/${VENV_NAME}/bin/activate
RPM_NAME=monitor-center
cd /opt/letv/${RPM_NAME}/packages
tar zxf setuptools-7.0.tar.gz 
tar zxf pip-8.1.2.tar.gz 
cd setuptools-7.0
python setup.py install
cd ..
cd pip-8.1.2
python setup.py install
cd ..
pip install ordereddict-1.1.tar.gz
pip install backports.ssl_match_hostname-3.5.0.1.tar.gz
pip install argparse-1.4.0-py2.py3-none-any.whl
pip install backports_abc-0.4-py2.py3-none-any.whl
pip install ipaddress-1.0.16.tar.gz
pip install six-1.10.0-py2.py3-none-any.whl
pip install singledispatch-3.4.0.3-py2.py3-none-any.whl
pip install requests-2.10.0-py2.py3-none-any.whl
pip install futures-3.0.5-py2-none-any.whl
pip install websocket_client-0.37.0.tar.gz 
pip install certifi-2016.2.28-py2.py3-none-any.whl
pip install tornado-4.3.tar.gz

#cd /opt/letv/falcon-agent && mkdir -p falcon-agent && tar zxf *.tar.gz -C ./falcon-agent --strip-components 1
#cd falcon-agent && python setup.py build && python setup.py install && cd -
cd /opt/letv/${RPM_NAME} && pip install *.tar.gz

chmod +x /etc/init.d/${RPM_NAME}
chkconfig --add ${RPM_NAME}

exit 0
