from remi import start
import os

from gellish_communicator.User_interface import Communicator


if __name__ == "__main__":
    heroku_port = int(os.environ['PORT'])
    start(Communicator, address='0.0.0.0', port=heroku_port, start_browser=False)
