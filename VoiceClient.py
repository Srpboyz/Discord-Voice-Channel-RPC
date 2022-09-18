from exceptions import NoClientGiven, NotSetup
from info import info
from Client import start_client
from typing import Tuple, List, Dict, Any
from time import sleep
from sys import exit
import pypresence
import asyncio


class VoiceClient:
    def __init__(self):
        self.start()
        self._paused = False

    def start(self) -> Tuple[pypresence.Client, str]:
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
                    self.__info = [None, None, None, None]
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
        self.__client.close()

    def pause(self) -> None:
        if not self._paused:
            self.__client.clear_activity()
            self.__info = [None, None, None, None]
        else:
            self.update()
        self._paused = not self._paused

    def get_peeps(self, *, voice_states: List[Dict[str, Any]]) -> List[str]:
        peeps = [
            user["user"]["username"]
            for user in voice_states
            if user["user"]["id"] != self.__id and not user["user"]["bot"]
        ]
        if len(peeps) == 1:
            return f"1 other person"
        if len(peeps) > 1:
            return f"{len(peeps)} other people"
        return None

    def get_vc(self) -> Tuple[str | None, str | None, str | None, str | None]:
        if not isinstance(self.__client, pypresence.Client):
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
            if not self._paused:
                self.update()
                sleep(10)

    def update(self) -> None:
        try:
            vc, guild, img, peeps = self.get_vc()
            if self.__info == [vc, guild, img, peeps]:
                return
            small_image = "https://c.tenor.com/TgKK6YKNkm0AAAAi/verified-verificado.gif"
            if img:
                if not guild and not self._paused:
                    self.__client.set_activity(
                        details=f"In a Voice Call",
                        large_image=img,
                        small_image=small_image,
                    )
                elif peeps and not self._paused:
                    self.__client.set_activity(
                        details=f"{guild} in {vc}",
                        state=f"with {peeps}",
                        large_image=img,
                        small_image=small_image,
                    )
                elif not self._paused:
                    self.__client.set_activity(
                        details=f"Listening in {guild}",
                        state=f"in {vc}",
                        large_image=img,
                        small_image=small_image,
                    )
            elif not self._paused:
                self.__client.clear_activity()
            if not self._paused:
                self.__info = [vc, guild, img, peeps]
        except (
            pypresence.exceptions.InvalidID,
            pypresence.exceptions.ServerError,
            pypresence.exceptions.DiscordError,
        ):
            self.stop()
            self.start()
        except NoClientGiven as e:
            exit(0)


if __name__ == "__main__":
    VoiceClient()
