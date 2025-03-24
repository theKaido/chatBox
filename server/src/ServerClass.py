import socket, select, json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Logger import info_log, warning_log, error_log
from Client import Client
from EventDispatcher import dispatch_on_receive
from Message import *

PORT = 8000
IP = '0.0.0.0'

class Server:

    def __init__(self):
        self.conn_counter = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.epoll = select.epoll()
        self.init_socket()
        self.init_epoll()
        self.clients = {}
        self.generate_key()

    def init_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind((IP, PORT))
        self.socket.listen(5)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def init_epoll(self):
        self.epoll.register(self.socket.fileno(), select.EPOLLIN)

    def generate_key(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        self.public_key = self.private_key.public_key()

        self.private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def generate_key_handshake(self, client):
        return generate_message_template(STATE_KEY_MESSAGE_SERVER, {
            "key": self.public_pem.decode("utf-8"),
            "token": client.get_token()
        })

    def init_connection(self):
        self.conn_counter = self.conn_counter + 1
        connection, address = self.socket.accept()
        connection.setblocking(False)

        info_log("Accepted connection from ", address)

        fd = connection.fileno()
        self.epoll.register(fd, select.EPOLLIN)
        self.clients[fd] = Client(connection, self.conn_counter)

    def shutdown(self):
        warning_log("Shutting down...")
        for k in self.clients:
            self.epoll.unregister(k)
            self.connections[k].connection.close()
        self.epoll.unregister(self.socket.fileno())
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.epoll.close()
        self.socket.close()

    def receive(self, fileno):
        byte_data = b""
        while 1:
            try:
                data = self.clients[fileno].connection.recv(128)
                if not data: break
                byte_data += data
            except BlockingIOError:
                break
        #If nothing received do nothing
        if(len(byte_data) == 0): return
        json_data = byte_data.decode('utf-8')
        try:
            json_message = json.loads(json_data)
            self.process_message(fileno, json_message)
        except Exception as e:
            error_log(e)

    def send(self, client, fileno):
        #warning_log("Send for", fileno)
        self.epoll.modify(fileno, select.EPOLLIN)
        client.send()


    def process_message(self, fileno, json_message):
        dispatch_on_receive(self, fileno, json_message)

    def serve(self):
        info_log("Started listening",IP,"on port", PORT)
        while True:
            events = self.epoll.poll(1)

            for connection_eno, event in events:
                if connection_eno == self.socket.fileno():
                    self.init_connection()
                elif event & select.EPOLLIN:
                    self.receive(connection_eno)
                elif event & select.EPOLLOUT:
                    self.send(self.clients[connection_eno], connection_eno)