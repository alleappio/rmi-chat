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
            "quit"
        ))
        if choice == 1:
            server_uri = utils.question("Server URI")
            self.client.server_uri = server_uri
            self.client.chat = Pyro5.api.Proxy(server_uri)
            self.client.chat.connect(self.client.uri, self.client.username)
            self.client.state = state.LOBBY
            self.just_entered = True
            return
        elif choice == 2:
            self.client.state = state.QUIT
            return

    def lobby(self):
        if self.just_entered:
            print(self.client.chat.welcome())
            self.just_entered = False
        choice = utils.menu((
            "enter channel",
            "channel list",
            "connected users",
            "quit"
        ))
        if choice == 1:
            channel = utils.question("insert the channel name")
            self.client.chat.enter_channel(self.client.uri, channel)
            self.client.current_channel = channel
            self.client.state = state.CHANNEL
            return
        elif choice == 2:
            print("Channel list:")
            for i in self.client.chat.get_channels():
                print(i)
            print("")
            return
        elif choice == 3:
            connected = self.client.chat.get_connected()
            print("connected users:")
            print(connected)
            return
        elif choice == 4:
            self.client.chat.leave(self.client.uri)
            self.client.state = state.DISCONNECTED
            return

    def channel(self):
        print(f"you are now in {self.client.current_channel}, type '/quit' to quit the channel and go back to the lobby")
        while self.client.state == state.CHANNEL:
            try:
                message = input("> ")
                if message == "/quit":
                    self.client.chat.leave_channel(self.client.uri)
                    self.client.state = state.LOBBY
                    return
                if message:
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

    def stateMachine(self):
        if self.client.state == state.DISCONNECTED:
            self.disconnected()

        elif self.client.state == state.LOBBY:
            self.lobby()

        elif self.client.state == state.CHANNEL:
            self.channel()

