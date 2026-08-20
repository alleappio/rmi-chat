import Pyro5.api
import tomllib as toml
from clientInfo import ClientInfo

clients = {}
channels = []

@Pyro5.api.expose
class Chat:
    def connect(self, uri, username):
        clients[uri] = ClientInfo(uri, username)
        self.broadcast("SYSTEM", f"{username} joined the server")

    def leave(self, uri):
        client = clients.get(uri)
        if client:
            clients.pop(uri)
            self.broadcast("SYSTEM", f"{client.username} left the chat")

    def send(self, uri, message):
        client = clients.get(uri)
        if client:
            self.broadcast(client.username, message)

    def broadcast(self, sender, message):
        dead_client = []
        for uri in clients:
            try:
                clients[uri].create_proxy().receive(sender, message)
                print(f"{sender}: {message}")
            except Exception as e:
                dead_client.append(uri)
                print(e)

        for i in dead_client:
            self.leave(i)

def load_config(filename):
    with open(filename, "r") as file:
        config = toml.loads(file.read())
    return config

def main():
    config = load_config("config.toml")
    channels = config["channels"]
    daemon = Pyro5.api.Daemon()
    uri = daemon.register(Chat, objectId=config["name"])

    print("Chat server:", uri)
    print("Run the client with this URI.")

    daemon.requestLoop()

if __name__ == '__main__':
    main()
