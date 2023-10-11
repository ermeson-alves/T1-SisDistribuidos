import socket
import threading
import smart_house_pb2 as proto
from .config import *
import struct

class Equipment:
    def __init__(self, dtype, name, ip, port) -> None:
        self.dtype = dtype
        self.name = name
        self.ip = ip
        self.port = port



    def send_identification(self):
        '''Essa função serve para enviar a identificação do equipamento, com nome, ip e porta'''

        # Escutar mensagem solicitante:
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
        # udp_client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # configurando o socket para se juntar ao grupo multicast
        udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # permite que o soquete compartilhe o mesmo endereço local
        
        udp_client_socket.bind((MULTICAST_GROUP, MULTICAST_PORT))
        mreq = struct.pack('4sL', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY) # cria estrutura dados de bytes 
        udp_client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # configurando o socket para se juntar ao grupo multicast

        i_send_identification = False # Aguarda solicitação de identificação
        while i_send_identification==False:
            data, addr = udp_client_socket.recvfrom(2024)
            msgn = proto.RequestIdentification()
            msgn.ParseFromString(data)
            if isinstance(msgn, proto.RequestIdentification): # Se o equipamento receber uma solicitação de identificação...
                print(msgn)
            
            # Enviar resposta:
            device_info = proto.DeviceInfo(
                        dtype=self.dtype,  # Defina o tipo do dispositivo (LAMP, TV, etc.)
                        name=self.name,
                        ip=self.ip,
                        port=self.port)
            
            identification_message = proto.GatewayMessage(type=proto.GatewayMessage.DEVICE_IDENTIFICATION, # Tipo de mensagem para o gateway
                                                          device_info=device_info)
            
            print(identification_message)
            self.send_msgn_TCP(identification_message, "Identificação enviada com sucesso!")
            # i_send_identification=True



    def send_msgn_TCP(self, msgn, sucess_msg="Mensagem enviada com sucesso!"):
        '''A mensagem é um tipo de mensagem definida com protocol buffers no aquivo .proto'''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((TCP_SERVER_ADDRESS, TCP_SERVER_PORT))
            print("Equipamento conectado ao gateway!")
            # Envie a mensagem e verifique se ocorreu um erro
            if s.sendall(msgn.SerializeToString()) is None:
                print(sucess_msg)
            else:
                print("Erro ao enviar a mensagem.")
        except Exception as e:
            print(f"Erro ao enviar a mensagem: {str(e)}")
        finally:
            s.close()



    def setup_server(self, th_function, str_server = ''):
        '''
        th_function é a função que escuta os comandos de ação recebidos
        str_server é a string exibida ao configurar o servidor TCP'''
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((self.ip, self.port))
        self.tcp_server.listen(3)
        print(str_server)
        threading.Thread(target=self.th_function).start()

    


    
