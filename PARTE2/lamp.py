import socket
import threading
import smart_house_pb2 as proto
from utils.config import *
from utils.equipmentClass import *
import struct



class Lamp(Equipment):
    # if gateway_message.type == proto.GatewayMessage.LAMP_CONTROL:
    #     self.is_on = gateway_message.lamp_control.is_on
    #     print(f"{self.name} is {'on' if self.is_on else 'off'}")

    def __init__(self, dtype, name, ip, port, is_on):
        super().__init__(dtype, name, ip, port)
        self.is_on = is_on


    def listen_for_commands(self):
        while True:
            client_socket, _ = self.tcp_server.accept()
            data = client_socket.recv(1024)
            if not data:
                break
            command = proto.LampControl()
            command.ParseFromString(data)
            self.is_on = command.is_on
            print(f"Lamp is {'on' if self.is_on else 'off'}")



if __name__ == "__main__":
    lamp = Lamp(dtype = proto.DeviceInfo.DeviceType.LAMP, 
                name = "Lamp 1",
                ip = '127.0.0.1',
                port = 7000,
                is_on = False)
    
    lamp.send_identification()
    lamp.setup_server("Lamp is ready to receive commands.")
    

