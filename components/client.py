import threading
import ssl
import websockets
from websockets.sync.client import connect

class WebSocketClient(threading.Thread):
    '''WebSocketThread will make websocket run in an a new thread'''
    def __init__(self, host, port, password, handler):
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.handler = handler
        self.client = None
        self.open = False
        # Initialize SSL context for secure connection
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def run(self):
        # Open the socket
        self.client = connect(f"wss://{self.host}:{self.port}", ssl_context=self.ssl_context, max_size=10**7)
        print("Client started.")
        #  Authenticate
        if self.authenticate():
            # If authenticated, signal open and recieve!
            self.open = True
            self.recieve()

    def stop(self):
        # Close the socket and signal closed!
        self.client.close()
        print("Client stopped.")
        self.open = False

    def authenticate(self):
        print("Authenticating...")
        # Send the password and recieve result
        self.client.send(self.password)
        response = self.client.recv()
        if response == "Authenticated":
            # If authenticated, return true
            print("Authenticated.")
            return True
        else:
            # If authentication fails, return false
            print("Authentication failed.")
            return False

    def send(self, msg):
        # Send a message through the socket
        self.client.send(msg)

    def recieve(self):
        # Try to iterate through messages.
        try:
            for message in self.client:
                # Handle the messages using the handler
                self.handler(message)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection error!")
        finally:
            # If connection closes one way or the another, notify and signal!
            print("Connection closed.")
            self.open = False