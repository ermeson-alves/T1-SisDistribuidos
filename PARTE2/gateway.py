import socket
from threading import Thread, Event
import struct
import smart_house_pb2 as proto
from utils.config import *
import logging
import signal


logging.basicConfig(filename="log/temp.log", filemode='w', encoding="utf-8", level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

class Gateway:
    def __init__(self):
        # Lista de dispositivos
        self.devices = []
        # Variaveis de controle
        self.is_running = True


        # Inicia servidor UDP para ser o receiver, com multicast, da temperatura:
        self.start_receiver_thread = Thread(target=self.start_receiver_temp)
        # Envia mensagem solicitando que equipamentos se identifiquem:
        self.send_disc_thread = Thread(target=self.send_discovery_messages)
        # Inicia o servidor tcp do processo do gateway:
        self.start_tcp_thread = Thread(target=self.start_tcp_server)
        # Inicia linha de comando da aplicação:
        self.command_line_thread = Thread(target=self.command_line_interface)

        # Inicia o servidor UDP que recebe a temperatura
        self.start_receiver_thread.start()

        self.start_tcp_thread.start()
        print(f"O servidor TCP do Gateway está esperando conexoes na porta{TCP_SERVER_PORT}\n")

        self.send_disc_thread.start()
        print("Gateway mandou a requisicao de identificacao...\n")
        
        self.command_line_thread.start()


    def start_receiver_temp(self):
        """Essa função serve para iniciar o servidor UDP que receberá as informações do
        sensor de temperatura. Baseado em: https://wiki.python.org/moin/UdpCommunication"""


        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Quando essa opção é configurada para 1, ela permite que você reutilize o mesmo endereço local em um novo soquete, mesmo que o endereço local ainda esteja sendo usado por outro soquete que está em processo de encerramento.
        sock.bind((MULTICAST_GROUP, MULTICAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.is_running:
            data = sock.recv(1024)
            msgn = proto.GatewayMessage()
            msgn.ParseFromString(data) # Decode
            if msgn.type==1: # se é uma mensagem de leitura de temperatura...
                temp = round(msgn.temp_reading.temperature, 2)
                logging.info(temp)
                self.temperature = temp



    def send_discovery_messages(self):
        """Essa função serve para utilizar o mecanismo de comunicação em grupo Multicast e assim
        descobrir os equipamentos inteligentes da casa"""

        ## Criar um UDP socket para enviar solicitação de identificação

        # udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL) # configurando a quantidade (2) de tempo ou de "saltos" pelo qual se estabelece que um pacote deve existir dentro de uma rede antes de ser descartado por um roteador

        # Enviar pedido de identificação:
        request_msgn = proto.RequestIdentification(msgn="Requested identification!")

        request_msgn_gateway = proto.GatewayMessage(type=proto.GatewayMessage.REQUEST_IDENTIFICATION, # Tipo de mensagem para o gateway
                                                    request_identification=request_msgn)
        
        udp_server_socket.sendto(request_msgn_gateway.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))
        


    def start_tcp_server(self, ip=TCP_SERVER_ADDRESS, port=TCP_SERVER_PORT, msgn=""):
        """Mensagem é a mensagem já devidamente codificada via mensagens protocol buffers definidas no arquivo .proto"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.listen(5)

        while self.is_running:
            conn, addr = s.accept()
            print(f"Conexão recebida de {addr}")
            data = conn.recv(1024)
            msgn = proto.GatewayMessage()
            msgn.ParseFromString(data) # Decode
            if not data: break
            
            if msgn.type==0:
                
                self.devices.append([int(msgn.device_info.dtype), msgn.device_info.name, msgn.device_info.ip, msgn.device_info.port])
                with open('dispositivos.txt', 'w') as f:
                    f.write(str(self.devices))

            conn.close()


    def command_line_interface(self):


        while self.is_running:
            print('T4')
            print("Interface de comando do Gateway:")
            print("1. Controlar lampada ('lamp:on' ou 'lamp:off')")
            print("2. Controlar canal da TV (tv)")
            print("3. Acessar temperatura (temp)")
            print("4. Sair")
            choice = input("Digite sua escolha: ")

            if choice.lower() == "sair":
                self.is_running = False
                break # é preciso encerrar todas as threads aqui
            elif choice.startswith("lamp:"):
                if choice == 'lamp:on':
                    command = 'on'
                else:
                    command = 'off'
                self.send_lamp_control(command)
            elif choice.lower() == "tv":
                canal = input("Digite o nome do canal: ")
                self.send_tv_channel(canal)
            elif choice.lower() == "temp":
                print("Temperatura atual: " + str(self.temperature))
            else:
                print("Comando invalido.")
    

    def send_lamp_control(self, command):

        if 0 in [device[0] for device in self.devices]:
            idx = self.devices.index(0) # indice da lampada
            print(self.devices[idx])
            ip, port = self.devices["LAMP"]
            lamp_control = proto.LampControl(is_on=(command == "on"))
            message = proto.GatewayMessage(type=proto.GatewayMessage.LAMP_CONTROL, lamp_control=lamp_control)
            self.send_message(ip, port, message)
        
        else:
            print("Não há lampadas funcionando!")

    def send_tv_channel(self, canal):
        if "TV" in self.devices:
            ip, port = self.devices["TV"]
            channel = proto.TvChannel(channel=canal)
            message = proto.GatewayMessage(type=proto.GatewayMessage.TV_CHANNEL, channel=channel)
            self.send_message(ip, port, message)

    def send_message(self, ip, port, message):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ip, port))
        tcp_socket.sendall(message.SerializeToString())
        tcp_socket.close()



if __name__ == "__main__":
    gateway = Gateway()
