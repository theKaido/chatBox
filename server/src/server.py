import socket, select
from ServerClass import Server

if __name__ == '__main__':
    try:
        server = Server()
        try:
            server.serve()
        except KeyboardInterrupt as e:
            server.shutdown()
    except Exception as e:
        print(e)