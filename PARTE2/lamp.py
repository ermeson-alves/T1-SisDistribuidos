import socket
import threading
import smart_house_pb2 as proto
from config import *
import struct

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

        # Escutar mensagem solicitante:
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
        # mcast_group = socket.inet_aton(MULTICAST_GROUP) # converte ip para o formato binario
        # udp_client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # configurando o socket para se juntar ao grupo multicast
        udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # configurando o socket para se juntar ao grupo multicast
        
        udp_client_socket.bind((MULTICAST_GROUP, MULTICAST_PORT))
        mreq = struct.pack('4sL', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # cria estrutura dados de bytes 
        udp_client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # configurando o socket para se juntar ao grupo multicast

        i_send_identification = False
        while i_send_identification==False:
            data, addr = udp_client_socket.recvfrom(2024)
            msgn = proto.RequestIdentification()
            msgn.ParseFromString(data)
            print(msgn)

        # Enviar resposta:
        identification_message = proto.DeviceInfo(name=self.name, ip=self.ip, port=self.port)
        udp_client_socket.sendto(identification_message.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))

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
