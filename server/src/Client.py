class Client:

    def __init__(self, connection):
        self.connection = connection

    def load_public_key(self, public_key):
        self.public_key = public_key