import remi.gui as gui
from remi.gui import *
from remi import start, App

class Communicator(App):
    def __init__(self, *args):
        super(Communicator, self).__init__(*args)

    def main(self):
        self.mainContainer = gui.Widget(margin='0px auto')
        self.mainContainer.set_size(1020, 600)
        self.menu = gui.Menu(width=620, height=30)
        m1 = gui.MenuItem('File', width=100, height=30)
        m11 = gui.MenuItem('Save', width=100, height=30)
        m12 = gui.MenuItem('Open', width=100, height=30)
        m12.onclick.connect(self.menu_open_clicked)
        m111 = gui.MenuItem('Save', width=100, height=30)
        m111.onclick.connect(self.menu_save_clicked)
        m112 = gui.MenuItem('Save as', width=100, height=30)
        m112.onclick.connect(self.menu_saveas_clicked)

        self.menu.append(m1)
        m1.append(m11)
        m1.append(m12)
        m11.append(m111)
        m11.append(m112)

        self.mainContainer.append(self.menu)

        # returning the root widget
        return self.mainContainer

    # listener functions
    def menu_open_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select an image file', False, '.')
        self.fileselectionDialog.confirm_value.connect(
            self.on_image_file_selected)
        self.fileselectionDialog.cancel_dialog.connect(
            self.on_dialog_cancel)
        # here is shown the dialog as root widget
        self.fileselectionDialog.show(self)

    def menu_save_clicked(self, widget):
        pass
        
    def menu_saveas_clicked(self, widget):
        pass


#--------------------------------------------------------------
# starts the webserver
if __name__ == "__main__":
    start(Communicator)
