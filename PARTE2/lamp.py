import socket
import threading
import smart_house_pb2 as proto
from config import *

class Lamp:
    def __init__(self):
        self.name='Lamp 1'
        self.ip = '127.0.0.1'
        self.port = 7000
        self.is_on = False

        self.send_identification()
        # self.setup_server()


    def send_identification(self):
        '''Essa função serve para enviar a identificação do equipamento, com nomo, ip e porta'''
        identification_message = proto.DeviceInfo(name=self.name, ip=self.ip, port=self.port)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(identification_message.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))

        print("Identificação enviada")
        # data, addr = self.tcp_socket.accept()
        # gateway_message = proto.GatewayMessage()
        # gateway_message.ParseFromString(data)

        # if gateway_message.type == proto.GatewayMessage.LAMP_CONTROL:
        #     self.is_on = gateway_message.lamp_control.is_on
        #     print(f"{self.name} is {'on' if self.is_on else 'off'}")



    def setup_server(self):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((self.ip, self.port))
        self.tcp_server.listen(1)
        print("Lamp is ready to receive commands.")
        threading.Thread(target=self.listen_for_commands).start()

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
    lamp = Lamp()
