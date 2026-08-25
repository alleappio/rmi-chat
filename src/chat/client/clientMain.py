import Pyro5.api
import os
import threading
import inquirer
import chat.common.state as state
import chat.common.utils as utils
import chat.client.client as client
import chat.client.stateMachine as stateMachine

def main():
    os.system("clear")
    name = utils.question("Your username")
    clientObj = client.Client()
    clientObj.username = name
    daemon = Pyro5.api.Daemon()
    client_uri = daemon.register(clientObj)
    clientObj.set_uri(client_uri)
    state_machine = stateMachine.StateMachine(clientObj)

    threading.Thread(
        target=daemon.requestLoop,
        daemon=True
    ).start()

    while clientObj.state != state.QUIT:
        try:
            state_machine.stateMachine()
        except Exception as e:
            # si blocca qui
            print(e)
            if clientObj.chat:
                clientObj.chat.leave(clientObj.uri)
            exit()

if __name__ == '__main__':
    main()
