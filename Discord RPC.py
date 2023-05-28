from VoiceClient import VoiceClient
from pystray import Icon, Menu as menu, MenuItem as item
from threading import Thread
from PIL import Image
from sys import exit
import os

from psutil import process_iter


class Tray:
    __slots__ = "rpc", "sysTrayIcon"

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
    processes = tuple(process.name() for process in process_iter())
    print(processes.count("Discord RPC.exe"))
    if processes.count("Discord RPC.exe") > 2:
        exit(0)
    del processes
    Tray()
