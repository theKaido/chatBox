from Message import STATE_KEY_MESSAGE_CLIENT, STATE_KEY_MESSAGE_SERVER, STATE_MESSAGE, STATE_ACK, STATE_NACK, generate_message_template
from Events import *

def dispatch_on_receive(server, fileno, json_message):
    message_state = json_message["state"]
    splitted = message_state.split(".")
    message_category = splitted[0]
    if(len(splitted) > 1):
        if message_state == STATE_KEY_MESSAGE_CLIENT:
            on_init_key_client(server, fileno, json_message)

