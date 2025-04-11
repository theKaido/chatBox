import socket, select
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from json_state import *
import threading
from datetime import datetime

class Client:
    def __init__(self, host='0.0.0.0', port=8000, username="default"):
        self.host = host
        self.port = port
        self.socket = None
        self.is_secure_canal = False
        self.init_key()
        self.connect()
        self.username = username
    
    def init_key(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        self.public_key = self.private_key.public_key()

        self.private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def connect(self):
        """Establishes a connection to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(False)
            print(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def send_raw_json(self, data):
        try:
            json_data = json.dumps(data)
            self.socket.sendall(json_data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")

    def send_json(self, data):
        if(not self.is_secure_canal):
            self.send_raw_json(data)
            return
        
        encrypted_payload = self.server_public_key_obj.encrypt(
            json.dumps(data).encode("utf-8"),
            padding.PKCS1v15()
        )

        self.socket.sendall(encrypted_payload)
    
    
    def receive_raw(self, buffer_size=1024):
        byte_data = b""

        ready = select.select([self.socket], [], [], 5000)
        if ready[0]:
            try:
                byte_data = self.socket.recv(buffer_size)
            except Exception as e:
                print(f"Receive error: {e}")

        if byte_data:
            try:
                json_message = json.loads(byte_data.decode('utf-8'))
                return json_message
            except json.JSONDecodeError:
                print("Erreur de décodage JSON")

        return None
    
    def receive(self, buffer_size=1024):
        byte_data = b""

        ready = select.select([self.socket], [], [], 5000)
        if ready[0]:
            try:
                byte_data = self.socket.recv(buffer_size)
            except Exception as e:
                print(f"Receive error: {e}")

        if byte_data:
            decrypted_message = self.private_key.decrypt(
                byte_data,
                padding.PKCS1v15()
            )
            return json.loads(decrypted_message.decode('utf-8'))

        return None

    def close(self):
        """Closes the connection."""
        if self.socket:
            self.send_json(generate_message_template(STATE_DISCONNECT, {"security-token": self.token}))
            self.socket.close()
            print("Connection closed.")

    def init_routine(self,dest_func=None):
        try:
            try:
                self.send_json(generate_message_template(STATE_KEY_MESSAGE_CLIENT, {
                    "key": self.public_pem.decode('utf-8')
                }))
                json_message = self.receive_raw()
                self.server_public_key = json_message["content"]["key"]
                self.server_public_key_obj = serialization.load_pem_public_key(self.server_public_key.encode())
                self.send_json(generate_message_template(STATE_AWAIT_TOKEN_CLIENT, {}))
                
                self.is_secure_canal = True
                
                json_message = self.receive()
                self.token = json_message["content"]["token"]
                self.send_json(generate_message_template(STATE_ACK, {"security-token": self.token}))
                self.display_fun = dest_func
                threading.Thread(target=self.run_listen_routine, daemon=True).start()
                if(self.display_fun == None):
                    self.run_send_routine()
            except ResourceWarning as e:
                print(e)
                self.init_routine(dest_func)
        except KeyboardInterrupt:
            self.close()
        except RuntimeError:
            print("Exiting...")

    def run_listen_routine(self):
        print("Started listening")
        while True:
            message = self.receive()
            if message == None: continue
            if message["state"] == STATE_MESSAGE:
                if(self.display_fun != None): self.display_fun(message["content"]["user"],message["content"]["message"])
                else:
                    user = message["content"]["user"]
                    msg = message["content"]["message"]
                    date = str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)
                    print(f"<{date}>[{user}] {msg}")
    
    def run_send_routine(self):
        while True:
            msg = input()
            date = str(datetime.now().hour)+':'+str(datetime.now().minute)+':'+str(datetime.now().second)
            self.send_msg(self.username, msg)
            print(f"<{date}>[{self.username}] {msg}")

    def send_msg(self, username, text):
        self.send_json(generate_message_template(STATE_MESSAGE, {"security-token": self.token, "user":username ,"message": text}))