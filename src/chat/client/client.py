import Pyro5.api
import chat.common.state as state

@Pyro5.api.expose
class Client:
    def __init__(self):
        self.state = state.DISCONNECTED
        self.username = ""
        self.server_uri = ""
        self.chat = Pyro5.api.Proxy
        self.current_channel = ""
        self.other_private = ""

    def set_uri(self, uri):
        self.uri = uri

    def receive(self, sender, message):
        print(f"\r{sender}: {message}")
        print("> ", end="", flush=True)

    def notify(self, message):
        print(f"SERVER: {message}")

    def quit_private(self):
        if self.state == state.PRIVATE:
            self.state = state.LOBBY
            # self.other_private = ""
