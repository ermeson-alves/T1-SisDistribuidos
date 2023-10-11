import socket
import threading
import struct
import json
import smart_house_pb2 as proto
from utils.config import *

class Gateway:
    def __init__(self):
        # Armazena informações dos Equipamentos
        self.devices = {} 
        # Envia mensagem solicitando que equipamentos se identifiquem:
        send_disc_thread = threading.Thread(target=self.send_discovery_messages)
        # Inicia o servidor tcp:
        start_tcp_thread = threading.Thread(target=self.start_tcp_server)
        # Inicia linha de comando da aplicação:
        command_line_thread = threading.Thread(target=self.command_line_interface)

        start_tcp_thread.start()
        print(f"The TCP Server is listening on the port {TCP_SERVER_PORT}\n")
        send_disc_thread.start()
        print("Gateway sent identification request...\n")
        command_line_thread.start()


    def send_discovery_messages(self):
        '''Essa função serve para utilizar o mecanismo de comunicação em grupo Multicast e assim
        descobrir os equipamentos inteligentes da casa'''

        # Criar um UDP socket para enviar solicitação de identificação
        MULTICAST_TTL = 2
        # udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL) # configurando o socket para se juntar ao grupo multicast

        # Enviar pedido de identificação:
        request_msgn = proto.RequestIdentification(msgn="Requested identification!")
        udp_server_socket.sendto(request_msgn.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))

        # Implementar lógica para receber a mensagens de identificação


    def start_tcp_server(self, ip=TCP_SERVER_ADDRESS, port=TCP_SERVER_PORT, msgn=''):
        '''Mensagem é a mensagem já devidamente codificada via mensagens protocol buffers definidas no arquivo .proto'''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            print(f"Conexão recebida de {addr}")
            data = conn.recv(2024)
            msgn = proto.GatewayMessage()
            msgn.ParseFromString(data) # Decode
            if not data: break
            
            conn.sendall(data.upper())
            conn.close()


    def command_line_interface(self):
        while True:
            print("Gateway Command Line Interface:")
            print("1. Control Lamp (e.g., 'lamp:on' or 'lamp:off')")
            print("2. Exit")
            choice = input("Enter your choice: ")

            if choice.lower() == 'exit':
                break
            elif choice.startswith('lamp:'):
                command = choice.split(':')[1]
                self.send_lamp_control(command)
            else:
                print("Invalid command.")
    

    def send_lamp_control(self, command):
        if 'lamp' in self.devices:
            ip, port = self.devices['lamp']
            lamp_control = proto.LampControl(is_on=(command == 'on'))
            message = proto.GatewayMessage(type=proto.GatewayMessage.LAMP_CONTROL, lamp_control=lamp_control)
            self.send_message(ip, port, message)

    def send_message(self, ip, port, message):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ip, port))
        tcp_socket.send(message.SerializeToString())
        tcp_socket.close()


if __name__ == "__main__":
    gateway = Gateway()
