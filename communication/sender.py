import socket
import json

PI_IP = "1"   # ← put your Pi IP
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect():
    client.connect((PI_IP, PORT))

def send_update(state=None, text=None):
    message = {
        "state": state,
        "text": text
    }
    client.send(json.dumps(message).encode())