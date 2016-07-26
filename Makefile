
coverage: test-install
	coverage run setup.py test
	coverage report --show-missing --include=flume*

integration: test-install
	python -m unittest discover -v -s test/integration

unit: test-install
	python -m unittest discover -v -s test/unit

install: requirements.txt flume/*
	python setup.py install

test-install: test-requirements.txt
	pip install -r test-requirements.txt
