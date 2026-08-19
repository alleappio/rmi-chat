import Pyro5.api

clients = {}


@Pyro5.api.expose
class Chat:
    def join(self, name, client_uri):
        clients[name] = client_uri
        self.broadcast("SYSTEM", f"{name} joined the chat")

    def leave(self, name):
        clients.pop(name, None)
        self.broadcast("SYSTEM", f"{name} left the chat")

    def send(self, sender, message):
        self.broadcast(sender, message)

    def broadcast(self, sender, message):
        for name, uri in list(clients.items()):
            try:
                client = Pyro5.api.Proxy(uri)
                client.receive(sender, message)
            except Exception:
                clients.pop(name, None)


daemon = Pyro5.api.Daemon()
uri = daemon.register(Chat)

print("Chat server:", uri)
print("Run the client with this URI.")

daemon.requestLoop()
