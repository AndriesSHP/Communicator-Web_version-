env:
	virtualenv env
	env/bin/pip install flake8

test: env
	env/bin/flake8
