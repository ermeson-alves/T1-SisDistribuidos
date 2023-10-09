import socket
import threading
import smart_house_pb2 as proto
from config import *

class TV:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 7060
        self.current_channel = "Channel 1"
        self.setup_server()

    def setup_server(self):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((self.ip, self.port))
        self.tcp_server.listen(1)
        print("TV is ready to receive channel change notifications.")
        threading.Thread(target=self.listen_for_channel_changes).start()

    def listen_for_channel_changes(self):
        while True:
            client_socket, _ = self.tcp_server.accept()
            data = client_socket.recv(1024)
            if not data:
                break
            channel_info = proto.TvChannel()
            channel_info.ParseFromString(data)
            self.current_channel = channel_info.channel
            print(f"TV is now playing {self.current_channel}")

if __name__ == "__main__":
    tv = TV()
