import Pyro5.api
import tomllib as toml
from chat.server.clientInfo import ClientInfo
from chat.server.chat import Chat

def load_config(filename):
    with open(filename, "r") as file:
        config = toml.loads(file.read())
    return config

def main():
    config = load_config("config/config.toml")
    channels = config["channels"]
    daemon = Pyro5.api.Daemon(host="0.0.0.0")
    chatObject = Chat()
    chatObject.channels = channels
    chatObject.welcomeMessage = config["welcome-message"]
    chatObject.verbose = config["verbose"]
    uri = daemon.register(chatObject, objectId=config["name"])

    print("Chat server:", uri)
    print("Run the client with this URI.")

    daemon.requestLoop()

if __name__ == '__main__':
    main()
