from Message import STATE_KEY_MESSAGE_CLIENT, STATE_KEY_MESSAGE_SERVER, STATE_MESSAGE, STATE_ACK, STATE_NACK, generate_message_template

def dispatch(server, fileno, json_message):
    message_state = json_message["state"]
    splitted = message_state.split(".")
    message_category = splitted(".")[0]
    print(json_message["content"]["key"])
    if(len(splitted) > 1):
        if message_category == STATE_KEY_MESSAGE_CLIENT:
            on_init_key_client(server, fileno, json_message)

def on_init_key_client(server,fileno,json_message):
    server.clients[fileno].load_public_key(json_message["content"]["key"])
    print(json_message)