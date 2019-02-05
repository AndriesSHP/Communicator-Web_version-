env:
	virtualenv env
	env/bin/pip install -r requirements/base.txt
	env/bin/pip install -r requirements/testing.txt

install: env

test: env
	env/bin/pytest
