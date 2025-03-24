import json
import select
from Logger import *
from Client import STATE_AWAIT_FOR_SERVER_KEY, STATE_AWAIT_FOR_SERVER_TOKEN, STATE_OK_TO_COM
from Message import *

def on_init_key_client(server,fileno,json_message):
    server.clients[fileno].load_public_key(json_message["content"]["key"])
    server_response = server.generate_key_handshake()
    server.clients[fileno].set_data(json.dumps(server_response))

def on_init_token_client(server, fileno, json_message):
    if(server.clients[fileno].state == STATE_AWAIT_FOR_SERVER_KEY): 
        server.clients[fileno].state = STATE_AWAIT_FOR_SERVER_TOKEN
    server_response = server.generate_token_answer(server.clients[fileno])
    server.clients[fileno].set_data(json.dumps(server_response))

def on_ack(server, fileno, json_message):
    if(server.clients[fileno].state == STATE_AWAIT_FOR_SERVER_TOKEN): 
        server.clients[fileno].state = STATE_OK_TO_COM
        warning_log("User " + server.clients[fileno].get_token() + " is now allowed to communicate securely.")
        return
    error_log("Got unauthorized user on the following token : " + server.clients[fileno].get_token() + ".")

def on_disconnect(server, fileno):
    server.pop_user(fileno)

def on_message(server, fileno, json_message):
    server.add_message(json_message["content"]["user"],json_message["content"]["message"],fileno)

def on_deny(server, fileno, token):
    server_response = generate_message_template(STATE_NACK, {
            "security-token": token })
    server.clients[fileno].set_data(json.dumps(server_response))

def callback(server,fileno):
    server.epoll.modify(fileno, select.EPOLLOUT)