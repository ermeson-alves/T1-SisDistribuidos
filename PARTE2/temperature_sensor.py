import socket
import threading
import smart_house_pb2 as proto
from utils.config import *
from utils.equipmetClass import *
import struct
import time 
import random


class TemperatureSensor(Equipment):

    # Implementar logica do envio continuo via multicast
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
    temp_sensor = TemperatureSensor(proto.DeviceInfo.DeviceType.TEMP_SENSOR,
                                    name="Sensor 1",
                                    ip="127.0.0.1",
                                    port=7030)
    
    temp_sensor.send_identification()
