from machine import Pin, I2C
import ssd1306
import time

# using default address 0x3C
i2c = I2C(0,sda=Pin(0, Pin.IN, Pin.PULL_UP), scl=Pin(1, Pin.IN, Pin.PULL_UP))
#i2c = I2C(0,sda=Pin(4), scl=Pin(5))
print(i2c.scan())
display = ssd1306.SSD1306_I2C(128, 64, i2c)

display.text('Hello, World!', 0, 0, 1)
display.show()

display.poweroff()
display.poweron()

display.contrast(0)
time.sleep(1)
display.contrast(255)
time.sleep(1)

display.invert(1)
time.sleep(1)
display.invert(0)
time.sleep(1)

display.rotate(True)
time.sleep(1)
display.rotate(False)
time.sleep(1)

display.fill(0)
display.fill_rect(0, 0, 32, 32, 1)
display.fill_rect(2, 2, 28, 28, 0)
display.vline(9, 8, 22, 1)
display.vline(16, 2, 22, 1)
display.vline(23, 8, 22, 1)
display.fill_rect(26, 24, 2, 4, 1)
display.text('MicroPython', 40, 0, 1)
display.text('SSD1306', 40, 12, 1)
display.text('OLED 128x64', 40, 24, 1)
display.show()