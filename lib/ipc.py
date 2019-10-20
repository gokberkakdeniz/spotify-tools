from os import path, makedirs, unlink
from threading import Thread
from pickle import loads as to_object, dumps as to_bytes, PickleError
from .exceptions import PlayerStateServerIsAlreadyRunningError, PlayerStateServerIsNotRunning
import socket

SOCKET_ADDRESS = "/tmp/spotifyctl/socket"


class ConnectionAccepterThread(Thread):
    def __init__(self, sock, connections):
        super().__init__()
        self.do_run = True
        self.sock = sock
        self.connections = connections

    def run(self):
        while self.do_run:
            try:
                connection, address = self.sock.accept()
                self.connections.append(connection)
            except socket.timeout:
                pass


class PlayerStateServer:
    def __init__(self):
        self.server_address = SOCKET_ADDRESS

        self._prepare_filesystem()

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(1)
        self._sock.bind(self.server_address)
        self._sock.listen(0)

        self._connections = list()

        self._thread = ConnectionAccepterThread(self._sock, self._connections)
        self._thread.start()

    def send(self, player_state):
        self._connections[:] = [conn for conn in self._connections if self._send(conn, player_state)]

    def shutdown(self):
        self._sock.close()
        unlink(self.server_address)

    def stop_accepter(self):
        self._thread.do_run = False

    def _send(self, connection, player_state):
        try:
            data = to_bytes(player_state)
            connection.send(data)
            return True
        except BrokenPipeError:
            return False

    def _prepare_filesystem(self):
        server_address_dirname = path.dirname(self.server_address)

        if not path.exists(server_address_dirname):
            makedirs(server_address_dirname)
        elif path.exists(self.server_address):
            if self._is_server_running():
                raise PlayerStateServerIsAlreadyRunningError()
            else:
                unlink(self.server_address)
        elif path.isfile(server_address_dirname):
            unlink(server_address_dirname)

    def _is_server_running(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            sock.close()
            return True
        except ConnectionRefusedError:
            return False

    def __del__(self):
        try:
            if hasattr(self, "_sock"):
                unlink(self.server_address)
        except FileNotFoundError:
            pass


class PlayerStateReceiver:
    def __init__(self):
        self.server_address = SOCKET_ADDRESS

        if not path.exists(self.server_address):
            raise PlayerStateServerIsNotRunning()

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._sock.connect(self.server_address)
        except ConnectionRefusedError:
            raise PlayerStateServerIsNotRunning()

    def start(self, callback):
        while True:
            try:
                data = self._sock.recv(4096)
                if not data:
                    raise PlayerStateServerIsNotRunning()

                try:
                    player_state = to_object(data)
                    callback(player_state)
                except PickleError:
                    print("error: malformed data received. closing...")
                    break
            except KeyboardInterrupt:
                print("closing...")
                break

    def __del__(self):
        if hasattr(self, "_sock"):
            self._sock.close()
