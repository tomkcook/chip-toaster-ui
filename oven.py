import serial
import struct
import time as pytime

class Oven():
    def __init__(self, tty):
        self.tty = tty
        self.serial = serial.Serial(tty, 115200, timeout=0.1)

    def process(self):
        while True:
            byte = self.serial.read()
            if len(byte) == 0:
                return False
            if byte[0] == 0x55:
                print(self.serial.readline().decode('utf-8'))
            elif byte[0] == 0x21:
                temp = struct.unpack('f', self.serial.read(4))[0]
                print('Temp = {}'.format(temp))
                return temp
            elif byte[0] == 0x32:
                frac = struct.unpack('f', self.serial.read(4))[0]
                print('Control fraction = {}'.format(frac))
            elif byte[0] in [0x22, 0x24, 0x28, 0x31, 0x32]:
                self.serial.read(4)

    def start(self, profile):
        while self.process():
            pass

        message = bytes([0x85])
        message += bytes([len(profile)])
        for (rate, target, time) in profile:
            message += struct.pack('<hhh', int(rate*100), int(target*100), int(time*100))
        message += bytes([0x85])
        print(' '.join('{:02x}'.format(x) for x in message))
        self.serial.write(message)
        pytime.sleep(0.5)

        while True:
            byte = self.serial.read()
            print(byte)
            if byte is None or len(byte) == 0:
                print('No response from oven')
                return False
            if byte[0] == 0x55:
                print(self.serial.readline().decode('utf-8'))
                continue
            if byte[0] == 0x18:
                return True
            if byte[0] == 0xFF:
                self.serial.read()
                print(self.serial.readline().decode('utf-8'))
                return False
            print('Unexpected message from oven: 0x{:02x}'.format(byte[0]))
            return False

    def stop(self):
        self.serial.write(0x95)
