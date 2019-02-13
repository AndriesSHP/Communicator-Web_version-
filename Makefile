env:
	virtualenv env
	env/bin/pip install .

testenv: env
	env/bin/pip install .[testing]

install: env

test: testenv
	env/bin/pytest
