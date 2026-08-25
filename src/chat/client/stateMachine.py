import sys
import Pyro5.api
import chat.client.client as client
import chat.common.utils as utils
import chat.common.state as state

class StateMachine:
    def __init__(self, clientObj: client.Client):
        self.client = clientObj
        self.just_entered = False

    def disconnected(self):
        choice = utils.menu((
            "connect to a server",
            "change username",
            "quit"
        ))
        if choice == 1:
            server_uri = utils.question("Server URI")
            self.client.server_uri = server_uri
            self.client.chat = Pyro5.api.Proxy(server_uri)
            result = self.client.chat.connect(self.client.uri, self.client.username)
            if result == 0:
                self.client.state = state.LOBBY
                self.just_entered = True
            else:
                print(f"Username {self.client.username} already in use, please choose another username")
            return
        elif choice == 2:
            name = utils.question("Your new username")
            self.client.username = name
        elif choice == 3:
            self.client.state = state.QUIT
            return

    def lobby(self):
        if self.just_entered:
            print(self.client.chat.welcome())
            self.just_entered = False
        choice = utils.menu((
            "Enter channel",
            "Enter private conversation",
            "Channel list",
            "Connected users",
            f"Private requests [{len(self.client.chat.get_private_requests(self.client.uri))}]",
            "Quit"
        ))
        if choice == 1:
            channel = utils.question("insert the channel name")
            self.client.chat.enter_channel(self.client.uri, channel)
            self.client.current_channel = channel
            self.client.state = state.CHANNEL
            return

        elif choice == 2:
            other_username =  utils.question("Insert others username")
            result = self.client.chat.enter_private(self.client.uri, other_username)
            if result == 0:
                self.other_private = other_username
                self.client.state = state.PRIVATE
            else:
                print(f"User {other_username} is not connected")

        elif choice == 3:
            print("Channel list:")
            for i in self.client.chat.get_channels():
                print(f"- {i}")
            print("")
            return

        elif choice == 4:
            connected = self.client.chat.get_connected()
            print("connected users:")
            for i in connected:
                print(f"- {i}")
            print("")
            return

        elif choice == 5:
            req = self.client.chat.get_private_requests(self.client.uri)
            print("private requests: ")
            for i in req:
                print(f"- {i}")
            print("")

        elif choice == 6:
            self.client.chat.leave(self.client.uri)
            self.client.state = state.DISCONNECTED
            return

    def channel(self):
        print(f"you are now in {self.client.current_channel}, type '/quit' to quit the channel and go back to the lobby")
        while self.client.state == state.CHANNEL:
            try:
                message = input("> ")
                if message == "/quit":
                    self.client.state = state.LOBBY
                    return
                if message:
                    sys.stdout.write("\033[F")
                    print(f"\r{self.client.username}: {message}", flush=True)
                    self.client.chat.send(self.client.uri, message)
            except KeyboardInterrupt:
                print("exit channel")
                self.client.state = state.LOBBY
                return
            except Exception as e:
                print(e)
                self.client.state = state.LOBBY
                return
        self.client.chat.leave_channel(self.client.uri)

    def private(self):
        print(f"you are now in a chat with {self.client.other_private}, type '/quit' to quit the channel and go back to the lobby")
        while self.client.state == state.PRIVATE:
            try:
                message = input("> ")
                if message == "/quit":
                    self.client.state = state.LOBBY
                    return
                if message:
                    sys.stdout.write("\033[F")
                    print(f"\r{self.client.username}: {message}", flush=True)
                    self.client.chat.send(self.client.uri, message)
            except KeyboardInterrupt:
                print("exit channel")
                self.client.state = state.LOBBY
                return
            except Exception as e:
                print(e)
                self.client.state = state.LOBBY
                return
        self.client.chat.leave_private(self.client.uri)

    def stateMachine(self):
        if self.client.state == state.DISCONNECTED:
            self.disconnected()

        elif self.client.state == state.LOBBY:
            self.lobby()

        elif self.client.state == state.CHANNEL:
            self.channel()

        elif self.client.state == state.PRIVATE:
            self.private()
