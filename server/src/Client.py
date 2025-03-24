import secrets
import string

class Client:

    def __init__(self, connection, counter):
        self.connection = connection
        self.data = ""
        random_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(15))
        self.token = str(counter)+random_secret

    def load_public_key(self, public_key):
        self.public_key = public_key

    def set_data(self, json_message):
        self.data = json_message

    def get_token(self):
        self.token

    def send(self):
        self.connection.send(self.data.encode('utf-8'))