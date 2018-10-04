[![Build Status](https://travis-ci.org/khink/Communicator-Web_version-.svg?branch=master)](https://travis-ci.org/khink/Communicator-Web_version-)

# Communicator-Web_version-
A web version of the Gellish Communicator App using RemiGUI
The Gellish Communicator project develops a stand-alone app that uses Tkinter for its GUI.
This project aim to develop a web based version that uses RemiGUI instead of Tkinter.
RemiGUI creates HTML and uses an ordaniry browser such as Safari to create and display input and output.
For the time being this is done in a separate repository, because this is an experimental version.


## Getting started

    pip install remi
    cd Web-Communicator
    python User_interface.py


## Tests

There are no test yet, but `make test` will check the project for coding style
(pep8) and superfluous imports. It uses flake8, which you can configure in
`setup.cfg`.
