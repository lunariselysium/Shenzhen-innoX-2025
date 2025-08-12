from machine import ADC, Pin
from time import sleep

class FlexSensor:
    def __init__(self, ioPin:int):
        self.p = Pin(ioPin, Pin.IN, Pin.PULL_DOWN)
    
    def calibrate(self, timeRange:int = 5, msInterval:int =100):
        pass
        
    
    def read(self):
        return self.p.value()

if __name__ == "__main__":
    fs = FlexSensor(3)
    fs.calibrate()
    while True:
        print(fs.read())
        sleep(0.1)