import socket
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fichier_json import generate_message_template, STATE_ACK, STATE_KEY_MESSAGE_CLIENT, STATE_KEY_MESSAGE_SERVER, STATE_MESSAGE, STATE_NACK

class Client:
    def __init__(self, host='polaris.xcxhollow.com', port=8000):
        self.host = host
        self.port = port
        self.socket = None
        self.connect()
    
    def connect(self):
        """Establishes a connection to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def send_json(self, data):
        try:
            json_data = json.dumps(data)
            self.socket.sendall(json_data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")
    
    
    def receive(self, buffer_size=1024):
        """Receives data from the server."""
        try:
            return self.socket.recv(buffer_size).decode('utf-8')
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None
    
    def close(self):
        """Closes the connection."""
        if self.socket:
            self.socket.close()
            print("Connection closed.")


# Example usage
if __name__ == "__main__":
    # Générer une clé privée RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Extraire la clé publique
    public_key = private_key.public_key()

    # Convertir la clé privée en chaîne PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Convertir la clé publique en chaîne PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    client = Client()
    try:
        client.send_json(generate_message_template(STATE_KEY_MESSAGE_CLIENT, {
            "key": public_pem.decode('utf-8')
        }))
        client.close()
    except KeyboardInterrupt:
        client.close()