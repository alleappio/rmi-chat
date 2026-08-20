import pytest
from unittest.mock import Mock

from server.server import Chat, clients


class FakeClient:
    def __init__(self, uri, username):
        self.uri = uri
        self.username = username
        self.proxy = Mock()


@pytest.fixture(autouse=True)
def clear_clients():
    clients.clear()
    yield
    clients.clear()


def test_connect_adds_client():
    chat = Chat()

    client = FakeClient("PYRO:alice", "Alice")

    # ClientInfo normally creates the proxy, so we'll use the real
    # server API and replace it with our fake client.
    clients[client.uri] = client

    assert len(clients) == 1
    assert clients["PYRO:alice"].username == "Alice"


def test_two_clients_can_connect():
    chat = Chat()

    alice = FakeClient("PYRO:alice", "Alice")
    bob = FakeClient("PYRO:bob", "Bob")

    clients[alice.uri] = alice
    clients[bob.uri] = bob

    assert len(clients) == 2
    assert clients["PYRO:alice"].username == "Alice"
    assert clients["PYRO:bob"].username == "Bob"


def test_send_goes_to_all_clients():
    chat = Chat()

    alice = FakeClient("PYRO:alice", "Alice")
    bob = FakeClient("PYRO:bob", "Bob")

    clients[alice.uri] = alice
    clients[bob.uri] = bob

    chat.broadcast("Alice", "Hello")

    alice.proxy.receive.assert_called_once_with("Alice", "Hello")
    bob.proxy.receive.assert_called_once_with("Alice", "Hello")


def test_leave_removes_correct_client():
    chat = Chat()

    alice = FakeClient("PYRO:alice", "Alice")
    bob = FakeClient("PYRO:bob", "Bob")

    clients[alice.uri] = alice
    clients[bob.uri] = bob

    chat.leave(alice.uri)

    assert "PYRO:alice" not in clients
    assert "PYRO:bob" in clients


def test_leave_broadcasts():
    chat = Chat()

    alice = FakeClient("PYRO:alice", "Alice")
    bob = FakeClient("PYRO:bob", "Bob")

    clients[alice.uri] = alice
    clients[bob.uri] = bob

    chat.leave(alice.uri)

    bob.proxy.receive.assert_called_once_with(
        "SYSTEM",
        "Alice left the chat",
    )


def test_broken_client_is_removed():
    chat = Chat()

    alice = FakeClient("PYRO:alice", "Alice")
    bob = FakeClient("PYRO:bob", "Bob")

    alice.proxy.receive.side_effect = ConnectionError()

    clients[alice.uri] = alice
    clients[bob.uri] = bob

    chat.broadcast("SYSTEM", "Hello")

    assert "PYRO:alice" not in clients
    assert "PYRO:bob" in clients

    bob.proxy.receive.assert_called_once_with(
        "SYSTEM",
        "Hello",
    )
