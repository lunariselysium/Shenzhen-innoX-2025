from machine import Pin, I2C, UART
import asyncio
import _thread
import bluetooth
import jy901b, flexsensor, ssd1306
from ble_midi_instrument import BLEMidi, NOTE
from flex_mapper import FlexSensorMapper

i2c = I2C(0, sda=Pin(21), scl=Pin(20))
ble = bluetooth.BLE()

display = ssd1306.SSD1306_I2C(128, 64, i2c)
imu = jy901b.JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=6)
midi = BLEMidi(ble, name="MIDIMitts")

mapper = FlexSensorMapper()

time_since_last_switch = 0

def draw_frame(display, primary_text: str, secondary_text: str):
    display.fill_rect(0, 0, 128, 16, 1)
    display.text(secondary_text, 0, 0, 0)
    display.text(primary_text, 0, 16, 1)

def initialize():
    display.poweron()
    display.contrast(255)
    display.fill(0)
    imu.set_output_types(["angles"])
    imu.save_settings()
    # Flex sensor calibration is now handled in FlexSensorMapper.__init__

async def main():
    global time_since_last_switch
    
    while True:
        primary_text = ""
        secondary_text = ""
        
        display.fill(0)
        imu.update()
        angles = imu.get_angles()
        #accel = imu.get_acceleration()
        #gyro = imu.get_angular_velocity()
        
        # Get triggered notes from the mapper
        triggered_notes = mapper.read(verbose=False)
        for note in triggered_notes:
            #_thread.start_new_thread(midi.send_note, (NOTE[note],))
            asyncio.create_task(midi.send_note(NOTE[note]))
            primary_text += (note + " ")
        if angles:
            #secondary_text = str(gyro['gy'])
            print(angles)
            if time_since_last_switch >= 2:
                if angles["pitch"] >= 45:
                    mapper.switch_left()
                elif angles["pitch"] <= -45:
                    mapper.switch_right()
            

        
        time_since_last_switch += 0.1
        
        draw_frame(display, primary_text, secondary_text)
        try:
            display.show()
        except BaseException as e:
            print(e)
        
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    initialize()
    asyncio.run(main())