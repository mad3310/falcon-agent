all:
	@echo "do nothing"

clean:
	rm -f `find . -type f -name '*.py[co]' `
	rm -fr dist
	rm -f  MANIFEST
	rm -fr falcon_agent.egg-info

rpm: build
	mkdir -p scripts/rpm/build/opt/letv/falcon-agent/ && \cp -f dist/*.tar.gz scripts/rpm/build/opt/letv/falcon-agent
	cd scripts/rpm && mkdir -p rpms && python build_rpm.py

build: clean
	python setup.py sdist

install: build
	cd dist && mkdir falcon_agent && tar zxf *.tar.gz -C ./falcon_agent --strip-components 1 && cd -
	virtualenv --no-site-packages dist/tmp
	. dist/tmp/bin/activate && pip install tornado==4.3 && pip install futures==3.0.5 && pip install elasticsearch==1.2.0
	. dist/tmp/bin/activate && cd dist/falcon_agent && python setup.py build && python setup.py install && cd -

.PHONY : all clean build install rpm
