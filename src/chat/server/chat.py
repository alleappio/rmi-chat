import Pyro5.api
from chat.server.clientInfo import ClientInfo

@Pyro5.api.expose
class Chat:
    clients = {}
    channels = []
    welcomeMessage = ""
    verbose = False

    def debug_log(self, message):
        if self.verbose:
            print(f"DEBUG: {message}")

    def get_uri_from_usernmae(self, username):
        for uri in self.clients:
            if self.clients[uri].username == username:
                return uri

    def connect(self, uri, username):
        self.clients[uri] = ClientInfo(uri, username)
        self.debug_log(f"{username} joined the server")
        self.notify_all(f"{username} joined the server")

    def leave(self, uri):
        client = self.clients.get(uri)
        if client:
            print(f"{client.username} left")
            self.clients.pop(uri)
            self.debug_log(f"{client.username} left the chat")

    def get_connected(self):
        clientsString = ""
        for i in self.clients:
            clientsString+=f"- {self.clients[i].username}\n"
        return clientsString

    def welcome(self):
        clientsString = self.get_connected()
        return f"{self.welcomeMessage}\nCurrently logged in:\n{clientsString}"

    def send(self, uri, message):
        client = self.clients.get(uri)
        if client:
            if client.in_channel:
                self.send_in_channel(client.username, message, client.channel)
            # self.debug_log(message)

    def notify_to_uri(self, uri, message):
        self.clients[uri].create_proxy().notify(message)

    def open_private(self, uri, other_username):
        other_uri = self.get_uri_from_usernmae(other_username)
        if other_uri in self.clients[uri].private_requests:
            #open connection between the two
            pass
        else:
            self.clients[other_uri].private_requests.append(uri)
            self.notify_to_uri(other_uri, f"{self.clients[uri].username} requested a private chat")

    def get_channels(self):
        return self.channels

    def enter_channel(self, uri, channel):
        client = self.clients.get(uri)
        if client:
            client.in_channel = True
            client.channel = channel
            if channel not in self.channels:
                self.channels.append(channel)

    def leave_channel(self, uri):
        client = self.clients.get(uri)
        if client:
            client.in_channel = False
            client.channel = ""

    def send_in_channel(self, sender, message, channel):
        dead_client = []
        for uri in self.clients:
            try:
                if self.clients[uri].in_channel and self.clients[uri].channel == channel and self.clients[uri].username != sender:
                    self.clients[uri].create_proxy().receive(sender, message)
                    self.debug_log(f"{sender}@{channel}: {message}")
            except Exception as e:
                dead_client.append(uri)
                print(e)

        for i in dead_client:
            self.debug_log(f"{self.clients[i].username} is dead")
            self.leave(i)

    def notify_all(self,message):
        dead_client = []
        for uri in self.clients:
            try:
                self.notify_to_uri(uri, message)
                print(f"NOTIFICATION: {message}")
            except Exception as e:
                dead_client.append(uri)
                print(e)

        for i in dead_client:
            self.debug_log(f"{self.clients[i].username} is dead")
            self.leave(i)

