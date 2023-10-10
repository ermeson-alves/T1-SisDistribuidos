import socket
import threading
import smart_house_pb2 as proto
from config import *
import struct

class TV:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 7060
        self.current_channel = "Channel 1"
        self.send_identification()
        self.setup_server()


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
