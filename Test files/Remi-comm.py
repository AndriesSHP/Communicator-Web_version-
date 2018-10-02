import remi.gui as gui
from remi import start, App


class Communicator(App):
    def __init__(self, *args):
        super(Communicator, self).__init__(*args)

    def main(self):
        container = gui.VBox(width = 200, height = 100)
        self.lbl = gui.Label('Hello world!')
        self.bt = gui.Button('Press me!')
        self.bt2 = gui.Button('Hello name surname!')

        # setting the listener for the onclick event of the button
        self.bt.onclick.connect(self.on_button_pressed)
        self.bt2.onclick.connect(self.on_button_pressed, "Name", "Surname")

        # appending a widget to another, the first argument is a string key
        container.append(self.lbl)
        container.append(self.bt)
        container.append(self.bt2)

        # returning the root widget
        return container

    # listener function
    def on_button_pressed(self, widget, name='', surname=''):
        self.lbl.set_text('Button pressed!')
        widget.set_text('Hello ' + name + ' ' + surname)

#--------------------------------------------------------------
# starts the webserver
if __name__ == "__main__":
    start(Communicator)
