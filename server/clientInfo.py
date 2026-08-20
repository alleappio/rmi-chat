import Pyro5.api

class ClientInfo:
    def __init__(self, uri, username):
        self.uri = uri
        self.username = username
        self.channel = None

    def create_proxy(self):
        return Pyro5.api.Proxy(self.uri)

    def __str__(self) -> str:
        return f"""client:\n uri: {self.uri}\n username: {self.username}\n channel: {self.channel}\n"""
