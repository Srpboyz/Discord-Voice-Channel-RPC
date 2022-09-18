from pystray import Icon, Menu as menu, MenuItem as item
from VoiceClient import VoiceClient
from threading import Thread
from PIL import Image
import os


class Tray:
    def __init__(self):
        self.rpc = VoiceClient()
        rpc = Thread(target=self.rpc.constant_update, args=())
        rpc.daemon = True
        menu_items = menu(
            item("Pause", self.rpc.pause, checked=lambda pause: self.rpc._paused),
            item("Quit", self.quit),
        )
        self.sysTrayIcon = Icon(
            "Discord RPC",
            icon=Image.open(rf"{os.getenv('LocalAppData')}\Discord\app.ico"),
            menu=menu_items,
        )
        rpc.start()
        self.sysTrayIcon.run()

    def quit(self):
        self.rpc.stop()
        self.sysTrayIcon.stop()


if __name__ == "__main__":
    Tray()
