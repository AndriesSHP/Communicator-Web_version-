import remi.gui as gui
from remi import start, App

import sys

class Communicator(App):

    def __init__(self, *args):
        super(Communicator, self).__init__(*args)
        self.net_name = "Gellish semantic network"

    # Define the main window
    def main(self):
        print('Net name:', self.net_name)
        self.container = gui.Widget(margin='0px auto')
        self.container.set_size(1020, 600)
        return self.container

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    start(Communicator)
