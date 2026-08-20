import Pyro5.api
from chat.server.clientInfo import ClientInfo

@Pyro5.api.expose
class Chat:
    clients = {}
    def connect(self, uri, username):
        self.clients[uri] = ClientInfo(uri, username)
        self.broadcast("SYSTEM", f"{username} joined the server")

    def leave(self, uri):
        client = self.clients.get(uri)
        if client:
            self.clients.pop(uri)
            self.broadcast("SYSTEM", f"{client.username} left the chat")

    def send(self, uri, message):
        client = self.clients.get(uri)
        if client:
            self.broadcast(client.username, message)

    def broadcast(self, sender, message):
        dead_client = []
        for uri in self.clients:
            try:
                self.clients[uri].create_proxy().receive(sender, message)
                print(f"{sender}: {message}")
            except Exception as e:
                dead_client.append(uri)
                print(e)

        for i in dead_client:
            self.leave(i)
