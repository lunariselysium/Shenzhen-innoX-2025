from machine import Pin, I2C, UART
import jy901b, flexsensor, ssd1306
from time import sleep
import bluetooth
from ble_midi_instrument import BLEMidi, NOTE

fs = flexsensor.FlexSensor(0)
#i2c = I2C(0,sda=Pin(0, Pin.IN, Pin.PULL_UP), scl=Pin(1, Pin.IN, Pin.PULL_UP))
i2c = I2C(0, sda=Pin(21), scl=Pin(20))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
uart = UART(1, baudrate=9600, tx=Pin(7), rx=Pin(6))
imu = jy901b.JY901B(uart)
ble = bluetooth.BLE()
midi = BLEMidi(ble, name="MIDIMitts")


fs.calibrate()
display.poweron()
display.contrast(255)
imu.set_output_types(["angles", "acceleration", "angular velocity"])

while True:
    fs_value = fs.read()
    imu.update()
    display.fill(0)
    
    angles=imu.get_angles()
    accel = imu.get_acceleration()
    gyro = imu.get_angular_velocity()
    
    if fs_value > 8000:
        display.fill_rect(0, 0, 128, 16, 1)
        midi.note_on(NOTE['C4'])
    else:
        midi.note_off(NOTE['C4'])
    
    display.show()
    
    print(fs_value)
    
    sleep(0.5)