import secrets
import string
import json
from Message import *
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

STATE_AWAIT_FOR_SERVER_KEY = 1
STATE_AWAIT_FOR_SERVER_TOKEN = 2
STATE_OK_TO_COM = 3


class Client:

    def __init__(self, connection, counter):
        self.connection = connection
        self.is_data_remaining = False
        self.data = ""
        random_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(15))
        self.token = str(counter)+random_secret
        self.public_key_obj = None
        self.state = STATE_AWAIT_FOR_SERVER_KEY
        self.mail_box = []

    def load_public_key(self, public_key):
        self.public_key = public_key.encode()
        self.public_key_obj = serialization.load_pem_public_key(self.public_key)

    def set_data(self, json_message):
        self.is_data_remaining = True
        self.data = json_message

    def get_token(self):
        return self.token
    
    def add_message(self, username, message):
        self.mail_box.append(generate_message_template(STATE_MESSAGE,{"security-token": self.token, "user": username ,"message": message}))

    def send_raw(self):
        self.connection.send(self.data.encode("utf-8"))

    def is_behind(self):
        return len(self.mail_box) > 0

    def send(self):
        if(self.is_data_remaining): self.is_data_remaining = False
        if(self.state == STATE_AWAIT_FOR_SERVER_KEY) : 
            self.send_raw()
            return
        
        encrypted_payload = self.public_key_obj.encrypt(
            self.data.encode("utf-8"),
            padding.PKCS1v15()
        )

        self.connection.send(encrypted_payload)

    def dispatch_mailbox(self):
        if(self.state == STATE_OK_TO_COM):
            while(len(self.mail_box) > 0):
                json_to_send = json.dumps(self.mail_box.pop(0))
                
                encrypted_payload = self.public_key_obj.encrypt(
                    json_to_send.encode("utf-8"),
                    padding.PKCS1v15()
                )

                self.connection.send(encrypted_payload)