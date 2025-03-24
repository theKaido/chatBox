import json
import select

def on_init_key_client(server,fileno,json_message):
    server.clients[fileno].load_public_key(json_message["content"]["key"])
    server_response = server.generate_key_handshake(server.clients[fileno])
    server.clients[fileno].set_data(json.dumps(server_response))
    server.epoll.modify(fileno, select.EPOLLOUT)