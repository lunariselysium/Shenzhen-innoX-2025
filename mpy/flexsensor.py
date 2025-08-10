from machine import ADC, Pin
from time import sleep

class flexSensor:
    def __init__(self, ioPin:int):
        self.ADC = ADC(Pin(ioPin))
        self.ADC.atten(ADC.ATTN_11DB)
        self.zeroValue = 1100
        self.value = 0
    
    def calibrate(self, timeRange:int = 5, msInterval:int =100):
        readings = []
        for i in range(timeRange):
            readings.append(self.ADC.read())
            sleep(msInterval/1000)
        self.zeroValue = int(sum(readings)/len(readings))
        
    
    def read(self):
        rawValue = self.ADC.read()
        self.value = abs(self.zeroValue-rawValue)
        return self.value

if __name__ == "__main__":
    fs = flexSensor(2)
    fs.calibrate()
    while True:
        print(fs.read())
        sleep(0.1)