import socket
import smart_house_pb2 as proto
from utils.config import *
from utils.equipmentClass import *
import time 
import random


class TemperatureSensor(Equipment):

    def __init__(self, dtype, name, ip, port, sampling_time):
        super().__init__(dtype, name, ip, port)
        self.sampling_time = sampling_time

    def start(self):
        while True:
            temperature_reading = proto.TemperatureReading(temperature=self.read_temperature())
            message = proto.GatewayMessage(type=proto.GatewayMessage.TEMPERATURE_READING, temp_reading=temperature_reading)
            self.send_message(message)
            time.sleep(self.sampling_time)

    def read_temperature(self):
        # Valor aleatório de temperatura (duas casas decimais)
        return random.uniform(18, 27)

    def send_message(self, msgn):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

        sock.sendto(msgn.SerializeToString(), (MULTICAST_GROUP, MULTICAST_PORT))

        

if __name__ == "__main__":
    temp_sensor = TemperatureSensor(proto.DeviceInfo.DeviceType.TEMP_SENSOR,
                                    name="Sensor 1",
                                    ip="127.0.0.1",
                                    port=7030,
                                    sampling_time=3) # sampling time representa o tempo, em segundos, que separa dados do sensor
    
    temp_sensor.send_identification()
    temp_sensor.start()
    # implementar logica do envio continuo
