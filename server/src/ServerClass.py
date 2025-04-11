import socket, select, json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from Logger import info_log, warning_log, error_log
from Client import Client, STATE_AWAIT_FOR_SERVER_KEY
from EventDispatcher import dispatch_on_receive
from Message import *

PORT = 8000
IP = '0.0.0.0'

class Server:

    def __init__(self, ip = IP, port = PORT):
        self.conn_counter = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.epoll = select.epoll()
        self.ip = ip
        self.port = port
        self.init_socket()
        self.init_epoll()
        self.clients = {}
        self.generate_key()

    def init_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind((self.ip, self.port))
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

    def generate_key_handshake(self):
        return generate_message_template(STATE_KEY_MESSAGE_SERVER, {
            "key": self.public_pem.decode("utf-8")
        })
    
    def generate_token_answer(self, client):
        return generate_message_template(STATE_KEY_TOKEN_SERVER, {
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

    def pop_user(self, fileno):
        try:
            self.clients[fileno].close()
            self.clients.pop(fileno)
        except Exception:
            try: self.clients.pop(fileno) 
            except Exception: return

    def add_message(self,username, message, fileno_sender):
        for client_eno, client in self.clients.items():
            if(client_eno == fileno_sender): continue
            client.add_message(username, message)


    def receive(self, fileno):
        if(self.clients[fileno].is_behind()):
            self.epoll.modify(fileno, select.EPOLLOUT)
            return
        byte_data = b""
        while 1:
            try:
                data = self.clients[fileno].connection.recv(128)
                if not data: break
                byte_data += data
            except BlockingIOError:
                break
            except Exception:
                try:
                    self.clients[fileno].connection.close()
                    self.clients.pop(fileno)
                    return
                except Exception:
                    self.clients.pop(fileno)
                    return
        #If nothing received do nothing
        if(len(byte_data) == 0): return

        if(self.clients[fileno].state != STATE_AWAIT_FOR_SERVER_KEY):
            byte_data = self.private_key.decrypt(
                byte_data,
                padding.PKCS1v15()
            )
        json_data = byte_data.decode('utf-8')
        try:
            json_message = json.loads(json_data)
            self.process_message(fileno, json_message)
        except Exception as e:
            #error_log(e)
            pass

    def send(self, client, fileno):
        client.send()
        self.epoll.modify(fileno, select.EPOLLIN)

    def dispatch_mbox(self):
        for client_eno, client in self.clients.items():
            client.dispatch_mailbox()

    def process_message(self, fileno, json_message):
        dispatch_on_receive(self, fileno, json_message)

    def serve(self):
        info_log("Started listening",self.ip,"on port", self.port)
        while True:
            events = self.epoll.poll(1)

            for connection_eno, event in events:
                if connection_eno == self.socket.fileno():
                    self.init_connection()
                elif event & select.EPOLLIN:
                    self.receive(connection_eno)
                elif event & select.EPOLLOUT:
                    self.send(self.clients[connection_eno], connection_eno)
            try:
                self.dispatch_mbox()
            except Exception:
                continue