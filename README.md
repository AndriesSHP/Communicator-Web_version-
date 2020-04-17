l[![Build Status](https://travis-ci.org/AndriesSHP/Communicator-Web_version-.svg?branch=master)](https://travis-ci.org/AndriesSHP/Communicator-Web_version-)

# Communicator-Web_enabled version
The Gellish Communicator project develops a reference application (the Gellish Communicator App) that supports the use any of the Formal Languages of the Gellish family of formalized natural languages, such as Formal English and Formal Dutch (Formeel Nederlands).
This web_enabled version aims to develop a version of the Gellish Communicator App that can be used stand-alone as well as via the web. This is realized by using REMI GUI library (https://github.com/dddomodossola/remi) instead of Tkinter for its GUI.
Remi GUI gets rendered in ordinary browsers, such as Safari or Edge. This allows to access the interface locally and remotely.
For the time being this web_enabled project uses its own repository.


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

### Local

The application can be run locally by downloading and installing Python3 and REMI and starting the main program.

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
