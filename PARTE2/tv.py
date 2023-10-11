import socket
import threading
import smart_house_pb2 as proto
from utils.config import *
from utils.equipmentClass import *
import struct


class TV(Equipment):
    def __init__(self, dtype, name, ip, port,current_channel):
        super().__init__(dtype, name, ip, port)
        self.current_channel = current_channel

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
    tv = TV(proto.DeviceInfo.DeviceType.TV,
            name="TV 1",
            ip="127.0.0.1",
            port=7060,
            current_channel="Channel 1")
    
    tv.send_identification()
    tv.setup_server(str_server="TV is ready to receive channel change notifications.")