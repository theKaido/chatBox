import socket, select
from ServerClass import Server

if __name__ == '__main__':
        ip = input("Entrez une adresse hôte\t %> ")
        port = -1 # default
        while port == -1:
            try:
                port = int(input("Entrez un port valide\t %> "))
            except Exception:
                continue
        server = Server(ip, port)
        try:
            server.serve()
        except KeyboardInterrupt as e:
            try: 
                server.shutdown()
            except Exception:
                 pass