import sys

from remi import start

from gellish_communicator.User_interface import (
    Communicator,
    Network,
)

if __name__ == "__main__":
    sys.setrecursionlimit(100000)

    net = Network()
    start(Communicator, title="Gellish Communicator")
