
coverage:
	coverage run setup.py test
	coverage report

integration:
	python -m unittest discover -v -s test/integration

benchmark:
	python -m unittest discover -v -s test/benchmark

unit:
	python -m unittest discover -v -s test/unit

install: requirements.txt flume/*
	python setup.py install

check-examples: examples
	python -m py_compile `find examples -name '*.py'`

test-install: test-requirements.txt
	pip install -r test-requirements.txt
