import Pyro5.api
import threading


@Pyro5.api.expose
class Client:
    def set_username(self, username):
        self.username = username

    def set_uri(self, uri):
        self.uri = uri

    def receive(self, sender, message):
        print(f"\n{sender}: {message}")
        print("> ", end="", flush=True)


def main():
    server_uri = input("Server URI: ")
    name = input("Your username: ")

    server = Pyro5.api.Proxy(server_uri)

    client = Client()
    client.set_username(name)
    daemon = Pyro5.api.Daemon()
    client_uri = daemon.register(client)
    client.set_uri(client_uri)

    threading.Thread(
        target=daemon.requestLoop,
        daemon=True
    ).start()

    server.connect(client_uri, name)

    try:
        while True:
            message = input("> ")

            if message == "/quit":
                break

            if message:
                server.send(client.uri, message)

    finally:
        server.leave(client.uri)

if __name__ == '__main__':
    main()
