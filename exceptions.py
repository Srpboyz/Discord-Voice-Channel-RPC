# for Client.py
class NoClientID(Exception):
    def __init__(self, message: str = None):
        if not message:
            message = "No Client ID given"
        super().__init__(message)


# for VoiceClient.py
class NotSetup(Exception):
    def __init__(self, message: str = None):
        if not message:
            message = "You haven't set up a client"
        super().__init__(message)


class NoClientGiven(Exception):
    def __init__(self, message: str = None):
        if not message:
            message = "No Client given"
        super().__init__(message)
