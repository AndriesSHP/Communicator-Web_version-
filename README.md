[![Build Status](https://travis-ci.org/AndriesSHP/Communicator-Web_version-.svg?branch=master)](https://travis-ci.org/AndriesSHP/Communicator-Web_version-)

# Communicator-Web_version
The Gellish Communicator project develops a reference application (the Gellish Communicator App) that supports the use any of the Formal Languages of the Gellish family of formalized natural languages, such as Formal English and Formal Dutch (Formeel Nederlands).
This related project aims to develop a web based version of the Gellish Communicator App that uses Remi GUI instead of Tkinter.
The Gellish Communicator project develops a stand-alone app that uses Tkinter for its GUI.
Remi GUI creates HTML and uses ordinary browsers, such as Safari or Edge, for creating and displaying input and output.
For the time being this project uses a separate repository.


## Getting started

    make install
    cd Web-Communicator
    python User_interface.py


## Tests

There are no test yet, but `make test` will check the project for coding style
(pep8) and superfluous imports. It uses flake8, which you can configure in
`setup.cfg`.
