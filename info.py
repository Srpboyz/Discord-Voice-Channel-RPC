from typing import Any, Dict
import json


def info() -> Dict[str, Any]:
    with open("C:/Shawn/Discord/info.json") as f:
        return json.load(f)


def set_token(id: str, token: str, refresh_token: str, start: str) -> None:
    data = info()
    data["VC"][id]["token"] = token
    data["VC"][id]["refresh_token"] = refresh_token
    data["VC"][id]["start"] = start
    with open("info.json", "w") as f:
        json.dump(data, f, indent=4)
