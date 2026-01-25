import os

import serial.tools.list_ports
from dotenv import load_dotenv



class Serial_helper():
    def __init__(self, vid, pid):
        self.vid = vid
        self.pid = pid

    def listPorts(self):
        for i in serial.tools.list_ports.comports():
            if i.serial_number != None:
                print(repr(i.pid), repr(i.vid), repr(i.device))
    
    def getUsbPort(self):
        for i in serial.tools.list_ports.comports():
            if i.pid == self.pid and i.vid == self.vid:
                return i.device
        return None

if __name__ == "__main__":
    pass



