from exceptions import NoClientID
from info import set_token
from datetime import datetime
from typing import Optional, Dict
from pypresence import Client
from sys import exit
import pypresence
import requests
import asyncio


def exchange_code(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> Dict:
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(
        url="https://discord.com/api/v10/oauth2/token", data=data, headers=headers
    )
    r.raise_for_status()
    return r.json()


def refresh_token(
    client_id: str, client_secret: str, refresh_token: str
) -> Dict[str, str]:
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(
        "https://discord.com/api/v10/oauth2/token", data=data, headers=headers
    )
    r.raise_for_status()
    return r.json()["access_token"], r.json()["refresh_token"]


def create_token(
    client: Client, client_id: str, client_secret: str, redirect_uri: str
) -> str:
    token = client.authorize(client_id, ["rpc"])
    token = token["data"]["code"]
    token = exchange_code(
        client_id=client_id,
        client_secret=client_secret,
        code=token,
        redirect_uri=redirect_uri,
    )
    return token["access_token"], token["refresh_token"]


def start_client(
    *,
    id: str = None,
    client_id: str = None,
    client_secret: str = None,
    token: str = None,
    r_token: str = None,
    start: str = None,
    redirect_uri: str = None,
    loop: Optional[asyncio.ProactorEventLoop] = None,
) -> Client:
    try:
        if not client_id:
            raise NoClientID()
        client = Client(client_id=client_id, loop=loop)
        client.start()
        if not token:
            token, r_token = create_token(
                client, client_id, client_secret, redirect_uri
            )
            start = datetime.now()
            start = start.strftime("%m-%d-%y %H:%M:%S")
            set_token(id, token, r_token, start)
        start = datetime.strptime(start, "%m-%d-%y %H:%M:%S")
        if (datetime.now() - start).total_seconds() >= 604800:
            token, r_token = refresh_token(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=r_token,
            )
            start = datetime.now()
            start = start.strftime("%m-%d-%y %H:%M:%S")
            set_token(id, token, r_token, start)
        client.authenticate(token)
        return client
    except (pypresence.exceptions.ServerError, pypresence.exceptions.DiscordError):
        return None
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        return None
