from pypresence import Client
from pypresence.exceptions import DiscordError, InvalidID, ServerError
from Client import start_client
from exceptions import NoClientGiven, NotSetup
from info import info
from typing import Tuple, List, Dict, Any
from time import sleep, time
from sys import exit
import asyncio


class VoiceClient:
    __slots__ = "__client", "__id", "__info", "__time", "_paused"

    def __init__(self):
        self.start()
        self.__time = None
        self._paused = False

    def start(self) -> Tuple[Client, str]:
        data = info()
        data = data.get("VC")
        if not data:
            raise NotSetup()
        while True:
            for id in data:
                client = start_client(
                    id=id,
                    client_id=data[id]["client_id"],
                    client_secret=data[id]["client_secret"],
                    token=data[id]["token"],
                    r_token=data[id]["refresh_token"],
                    start=data[id]["start"],
                    redirect_uri=data[id]["redirect_uri"],
                )
                if client:
                    self.__client, self.__id = client, id
                    self.__info = (None, None, None, None)
                    return
            if not client:
                sleep(3)

    def stop(self) -> None:
        if not self.__client:
            raise NoClientGiven()
        try:
            self.__client.clear_activity()
        except:
            pass
        self.__time = None
        self.__client.close()

    def pause(self) -> None:
        if not self._paused:
            self.__client.clear_activity()
            self.__info = (None, None, None, None)
            self.__time = None
        else:
            self.update()
        self._paused = not self._paused

    def get_peeps(self, *, voice_states: List[Dict[str, Any]]) -> str:
        peeps = [
            user["user"]["username"]
            for user in voice_states
            if user["user"]["id"] != self.__id and not user["user"]["bot"]
        ]
        if not peeps:
            return None
        return f"{len(peeps)} other people"

    def get_vc(self) -> Tuple[str | None, str | None, str | None, str | None]:
        if not isinstance(self.__client, Client):
            raise NoClientGiven(
                f"Client must of type pypresence.Client not {type(self.__client)}"
            )
        vc = self.__client.get_selected_voice_channel()
        if vc["data"]:
            if vc["data"]["guild_id"]:
                peeps = self.get_peeps(voice_states=vc["data"]["voice_states"])
                guild = self.__client.get_guild(vc["data"]["guild_id"])
                img = guild["data"].get("icon_url")
                if not img:
                    img = "https://yt3.ggpht.com/ytc/AMLnZu99EohaiHwRF_jqYR-uhpFjBNbVg1VuvmNWTVv_sw=s900-c-k-c0x00ffffff-no-rj"
                guild = guild["data"]["name"]
                return vc["data"]["name"], guild, img, peeps
            img = "https://yt3.ggpht.com/ytc/AMLnZu99EohaiHwRF_jqYR-uhpFjBNbVg1VuvmNWTVv_sw=s900-c-k-c0x00ffffff-no-rj"
            return None, None, img, None
        return None, None, None, None

    def constant_update(self) -> None:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            self.update()
            sleep(15)

    def update(self) -> None:
        try:
            if self._paused:
                return
            vc, guild, img, peeps = self.get_vc()
            if self.__info == (vc, guild, img, peeps):
                return
            small_image = "https://c.tenor.com/TgKK6YKNkm0AAAAi/verified-verificado.gif"
            if img:
                if not self.__time:
                    self.__time = time()
                if not guild:
                    details = "In a Voice Call"
                    state = None
                elif peeps:
                    details = f"{guild} in {vc}"
                    state = f"with {peeps}"
                else:
                    details = f"Listening in {guild}"
                    state = f"in {vc}"

                self.__client.set_activity(
                    details=details,
                    state=state,
                    large_image=img,
                    small_image=small_image,
                    start=self.__time,
                )
            else:
                self.__client.clear_activity()
                self.__time = None
            self.__info = (vc, guild, img, peeps)
        except (InvalidID, ServerError, DiscordError):
            self.stop()
            self.start()
        except NoClientGiven:
            self.__time = None
            exit(0)
        except:
            return


if __name__ == "__main__":
    VoiceClient()
