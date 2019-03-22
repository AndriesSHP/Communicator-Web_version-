import remi.gui as gui
from remi import start, App
import os

class MyApp(App):
    def main(self):
        main_container = gui.VBox(width=300, height=200, style={'margin':'0px auto'})
        return main_container

if __name__ == "__main__":
    heroku_port = int(os.environ['PORT'])
    start(MyApp, address='0.0.0.0', port=heroku_port, start_browser=False)
