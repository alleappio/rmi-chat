import Pyro5.api
import threading
from chat.common.state import State


@Pyro5.api.expose
class Client:
    def __init__(self):
        self.state = State.DISCONNECTED
        self.username = ""
        self.server_uri = ""
        self.chat = Pyro5.api.Proxy

    def set_uri(self, uri):
        self.uri = uri

    def receive(self, sender, message):
        print(f"\n{sender}: {message}")
        print("> ", end="", flush=True)

def menu(options: tuple):
    for i in options:
        print(i)
    choice = int(input("> "))
    return choice

def state_machine(client):
    if client.state == State.DISCONNECTED:
        choice = menu((
            "1. connect to a server",
            "2. quit"
        ))
        if choice == 1:
            server_uri = input("Server URI: ")
            client.server_uri = server_uri
            client.chat = Pyro5.api.Proxy(server_uri)
            client.chat.connect(client.uri, client.username)
            client.state = State.LOBBY
            return
        elif choice == 2:
            client.state = State.QUIT
            return

    elif client.state == State.LOBBY:
        print(client.chat.welcome())
        choice = menu((
            "1. enter channel",
            "2. channel list",
            "3. quit"
        ))
        if choice == 1:
            channel = str(input("insert the channel name: "))
            client.chat.enter_channel(client.uri, channel)
            client.state = State.CHANNEL
            return
        elif choice == 2:
            print(client.chat.get_channels())
            return
        elif choice == 3:
            client.chat.leave(client.uri)
            client.state = State.DISCONNECTED
            return

    elif client.state == State.CHANNEL:
        print("you are now in a channel, type '/quit' to quit the channel and go back to the lobby")
        while True:
            message = input("> ")
            if message == "/quit":
                client.chat.leave_channel(client.uri)
                client.state = State.LOBBY
                return
            if message:
                client.chat.send(client.uri, message)



def main():
    name = input("Your username: ")
    client = Client()
    client.username = name
    daemon = Pyro5.api.Daemon()
    client_uri = daemon.register(client)
    client.set_uri(client_uri)

    threading.Thread(
        target=daemon.requestLoop,
        daemon=True
    ).start()

    while client.state != State.QUIT:
        try:
            state_machine(client)
        except Exception as e:
            print(e)
        finally:
            client.chat.leave(client.uri)

if __name__ == '__main__':
    main()
