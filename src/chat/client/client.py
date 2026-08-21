import Pyro5.api
import os
import threading
import inquirer
from chat.common.state import State
import chat.common.utils as utils


@Pyro5.api.expose
class Client:
    def __init__(self):
        self.state = State.DISCONNECTED
        self.username = ""
        self.server_uri = ""
        self.chat = Pyro5.api.Proxy
        self.just_entered = False

    def set_uri(self, uri):
        self.uri = uri

    def receive(self, sender, message):
        print(f"\r{sender}: {message}")
        print("> ", end="", flush=True)


def state_machine(client):
    if client.state == State.DISCONNECTED:
        choice = utils.menu((
            "1. connect to a server",
            "2. quit"
        ))
        if choice == 1:
            # server_uri = input("Server URI: ")
            server_uri = utils.question("Server URI")
            client.server_uri = server_uri
            client.chat = Pyro5.api.Proxy(server_uri)
            client.chat.connect(client.uri, client.username)
            client.state = State.LOBBY
            client.just_entered = True
            return
        elif choice == 2:
            client.state = State.QUIT
            return

    elif client.state == State.LOBBY:
        if client.just_entered:
            print(client.chat.welcome())
            client.just_entered = False
        choice = utils.menu((
            "1. enter channel",
            "2. channel list",
            "3. quit"
        ))
        if choice == 1:
            channel = utils.question("insert the channel name")
            client.chat.enter_channel(client.uri, channel)
            client.state = State.CHANNEL
            return
        elif choice == 2:
            for i in client.chat.get_channels():
                print(i)
            return
        elif choice == 3:
            client.chat.leave(client.uri)
            client.state = State.DISCONNECTED
            return

    elif client.state == State.CHANNEL:
        print("you are now in a channel, type '/quit' to quit the channel and go back to the lobby")
        while client.state == State.CHANNEL:
            try:
                message = input("> ")
                if message == "/quit":
                    client.chat.leave_channel(client.uri)
                    client.state = State.LOBBY
                    return
                if message:
                    print(f"\r{client.username}: {message}", flush=True)
                    client.chat.send(client.uri, message)
            except KeyboardInterrupt:
                print("exit channel")
                client.state = State.LOBBY
                return
            except Exception as e:
                print(e)
                client.state = State.LOBBY
                return



def main():
    os.system("clear")
    name = utils.question("Your username")
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
            if client.chat:
                client.chat.leave(client.uri)

if __name__ == '__main__':
    main()
