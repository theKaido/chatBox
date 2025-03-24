from Message import *
from Events import *

def dispatch_on_receive(server, fileno, json_message):
    message_state = json_message["state"]
    splitted = message_state.split(".")
    message_category = splitted[0]
    print(json_message)
    if message_state != STATE_KEY_MESSAGE_CLIENT and message_state != STATE_AWAIT_TOKEN_CLIENT:
        try:
            if not check_auth(server, fileno, json_message):
                on_deny(server, fileno, json_message["content"]["security-token"]) 
                callback(server, fileno)
        except Exception as e:
            on_deny(server, fileno, "")
            callback(server, fileno)
            
    if message_state == STATE_KEY_MESSAGE_CLIENT:
        on_init_key_client(server, fileno, json_message)
    if message_state == STATE_AWAIT_TOKEN_CLIENT:
        on_init_token_client(server, fileno, json_message)
    if message_state == STATE_ACK:
        on_ack(server, fileno, json_message)
    if message_state == STATE_MESSAGE:
        on_message(server, fileno, json_message)
    if message_state == STATE_DISCONNECT:
        on_disconnect(server, fileno)
    callback(server, fileno)

def check_auth(server, fileno, json_message):
    return server.clients[fileno].token == json_message["content"]["security-token"]