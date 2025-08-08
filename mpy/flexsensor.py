from machine import ADC, Pin
from time import sleep


class flexSensor:
    """
    弯曲传感器类
    
    用于读取弯曲传感器的模拟值并进行处理的类，可以校准零点并读取弯曲变化值。
    
    Attributes:
        ADC: ADC对象，用于读取模拟引脚的值
        zeroValue (int): 校准后的零点值
        value (int): 当前传感器读数与零点值的差值
    """
    def __init__(self, ioPin: int):
        """
        初始化弯曲传感器
        
        Args:
            ioPin (int): 连接传感器的GPIO引脚号
        """
        self.ADC = ADC(Pin(ioPin))
        self.ADC.atten(ADC.ATTN_11DB)
        self.zeroValue = 1100
        self.value = 0

    def calibrate(self, timeRange: int = 5, msInterval: int = 100):
        """
        校准传感器，获取零点值
        
        在指定时间内多次读取传感器值，计算平均值作为零点值。
        
        Args:
            timeRange (int): 采样次数，默认为5次
            msInterval (int): 每次采样间隔(毫秒)，默认为100毫秒
        """
        readings = []
        for i in range(timeRange):
            readings.append(self.ADC.read())
            sleep(msInterval / 1000)
        self.zeroValue = int(sum(readings) / len(readings))

    def read(self):
        """
        读取传感器当前值
        
        读取传感器的原始值，并计算与零点值的差值绝对值。
        
        Returns:
            int: 当前读数与零点值的绝对差值
        """
        rawValue = self.ADC.read()
        self.value = abs(self.zeroValue - rawValue)
        return self.value


if __name__ == "__main__":
    # 创建传感器实例并进行校准
    fs = flexSensor(3)
    fs.calibrate()
    # 循环读取并打印传感器值
    while True:
        print(fs.read())
        sleep(0.1)