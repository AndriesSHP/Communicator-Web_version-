[![Build Status](https://travis-ci.org/AndriesSHP/Communicator-Web_version-.svg?branch=master)](https://travis-ci.org/AndriesSHP/Communicator-Web_version-)

# Communicator-Web_version
The Gellish Communicator project develops a reference application (the Gellish Communicator App) that supports the use any of the Formal Languages of the Gellish family of formalized natural languages, such as Formal English and Formal Dutch (Formeel Nederlands).
This related project aims to develop a web based version of the Gellish Communicator App that uses Remi GUI instead of Tkinter.
The Gellish Communicator project develops a stand-alone app that uses Tkinter for its GUI.
Remi GUI creates HTML and uses ordinary browsers, such as Safari or Edge, for creating and displaying input and output.
For the time being this project uses a separate repository.


## Getting started

    make install
    python main.py


## Tests

Run `make test`.

This will:

- Check the project for coding style and superfluous imports.
  It uses flake8, which you can configure in `setup.cfg`.
- Run unit tests, of which there currently is only one.


## Deployment

### Heroku

The project is [Heroku](https://heroku.com/)-enabled.

Short Remi-specific-instructions [source](https://github.com/dddomodossola/remi/issues/280#issuecomment-465346938):

- Download Heroku console [Heroku setup](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
- Run `heroku login`
- Open the [Heroku dashboard](https://dashboard.heroku.com/apps)
- Create a new App named `gellish<X>`, where X can be anything (but `gellish` is taken)
- In your copy of this repository, add the Heroku remote: `https://git.heroku.com/gellish<X>.git`
- Run `git push heroku master`
- Run `heroku ps:scale web=1`
- Run `heroku open`
