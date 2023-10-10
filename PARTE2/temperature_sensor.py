import socket
import time
import smart_house_pb2 as proto
import random
import struct 
from config import *

class TemperatureSensor:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 7030

    def send_identification(self):
        '''Essa função serve para enviar a identificação do equipamento, com nomo, ip e porta'''

        # Escutar mensagem solicitante:
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
        # mcast_group = socket.inet_aton(MULTICAST_GROUP) # converte ip para o formato binario
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

    def start(self):
        while True:
            temperature_reading = proto.TemperatureReading(temperature=self.read_temperature())
            message = proto.GatewayMessage(type=proto.GatewayMessage.TEMPERATURE_READING, temp_reading=temperature_reading)
            self.send_message(message)
            time.sleep(1)

    def read_temperature(self):
        # Valor aleatório de temperatura
        return round(random.uniform(18, 27), 2)

    def send_message(self, message):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.SerializeToString(), (self.ip, self.port))
        udp_socket.close()

if __name__ == "__main__":
    temp_sensor = TemperatureSensor()
    temp_sensor.start()
