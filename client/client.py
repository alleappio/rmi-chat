import Pyro5.api
import threading


@Pyro5.api.expose
class Client:
    def receive(self, sender, message):
        print(f"\n{sender}: {message}")
        print("> ", end="", flush=True)


server_uri = input("Server URI: ")
name = input("Your name: ")

server = Pyro5.api.Proxy(server_uri)

client = Client()
daemon = Pyro5.api.Daemon()
client_uri = daemon.register(client)

threading.Thread(
    target=daemon.requestLoop,
    daemon=True
).start()

server.join(name, client_uri)

try:
    while True:
        message = input("> ")

        if message == "/quit":
            break

        if message:
            server.send(name, message)

finally:
    server.leave(name)
