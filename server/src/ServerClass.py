import socket, select
from Logger import info_log, warning_log, error_log

PORT = 8000
IP = '0.0.0.0'

class Server:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.epoll = select.epoll()
        self.init_socket()
        self.init_epoll()
        self.connections = {}

    def init_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind((IP, PORT))
        self.socket.listen(5)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def init_epoll(self):
        self.epoll.register(self.socket.fileno(), select.EPOLLIN)

    def init_connection(self):
        connection, address = self.socket.accept()
        connection.setblocking(False)

        info_log("Accepted connection from ", address)

        fd = connection.fileno()
        self.epoll.register(fd, select.EPOLLIN)
        self.connections[fd] = connection
        #requests[fd] = ''
        #responses[fd] = ''

    def shutdown(self):
        warning_log("Shutting down...")
        for k in self.connections:
            self.epoll.unregister(k)
            self.connections[k].close()
        self.epoll.unregister(self.socket.fileno())
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.epoll.close()
        self.socket.close()

    def receive(self, fileno):
        warning_log("Received from", fileno)
        self.epoll.modify(fileno, select.EPOLLOUT)
        wholedata = ""
        while 1:
            try:
                data = self.connections[fileno].recv(128)
                if not data: break
                wholedata += data.decode('utf-8', errors='ignore')
            except BlockingIOError:
                break
        info_log("Received :", wholedata.replace("\n",""))

    def send(self, fileno):
        warning_log("Send for", fileno)
        self.epoll.modify(fileno, select.EPOLLIN)

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
                    self.send(connection_eno)