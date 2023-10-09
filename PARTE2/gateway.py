import socket
import threading
import struct
import json
import smart_house_pb2 as proto
from config import *

class Gateway:
    def __init__(self):
        # Armazena informações dos Equipamentos
        self.devices = {} 
        # Envia mensagem solicitando que equipamentos se identifiquem
        receive_id_thread = threading.Thread(target=self.receive_identification_messages)
        # Inicia linha de comando da aplicação
        command_line_thread = threading.Thread(target=self.command_line_interface)

        receive_id_thread.start()
        command_line_thread.start()


    def receive_identification_messages(self):
        '''Essa função serve para utilizar o mecanismo de comunicação em grupo Multicast e assim
        descobrir os equipamentos inteligentes da casa'''

        # Create a UDP socket para enviar solicitação de identificação
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        
        # Bind to the server address
        udp_socket.bind((MULTICAST_GROUP, MULTICAST_PORT))

        # Set up multicast group
        mcast_group = socket.inet_aton(MULTICAST_GROUP) # converte ip para o formato binario
        mreq = struct.pack('4sL', mcast_group, socket.INADDR_ANY) # cria estrutura dados de bytes 
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # configurando o socket para se juntar ao grupo multicast

        print("Gateway is waiting for device identification messages...")

        # Enviar pedido de identificação:
        # request_msgn = proto.RequestIdentification(msgn="Requested identification!")
        # udp_socket.sendto(request_msgn.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))

        while True:
            data, addr = udp_socket.recvfrom(2024)
            device_info = proto.DeviceInfo()
            device_info.ParseFromString(data)
            self.devices[device_info.name] = (device_info.ip, device_info.port)
            print(f"Device {device_info.name} identified with IP {device_info.ip}, Port {device_info.port}")
            with open('./dispositivos.txt', 'w') as f: 
                f.write(json.dumps(self.devices))



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
