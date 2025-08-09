import time
from machine import Pin, I2C
import bluetooth
import jy901b, neopixel
from ble_midi_instrument import BLEMidi, NOTE
from flex_mapper import FlexSensorMapper
from display_manager import DisplayManager


i2c = I2C(0, sda=Pin(11), scl=Pin(10))
ble = bluetooth.BLE()

led = neopixel.NeoPixel(Pin(38, Pin.OUT), 1)
imu = jy901b.JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=8)
midi = BLEMidi(ble, name="MIDIMitts")
mapper = FlexSensorMapper()
disp = DisplayManager(i2c)


def handle_imu_switching(angles, last_switch_time, mapper, cooldown_ms=500, threshold=30, reverse:bool=False):
    """Handle IMU-based switching based on pitch angle, with a set cooldown. Left/right can be reversed"""
    current_time = time.ticks_ms()
    if current_time - last_switch_time >= cooldown_ms:
        if (angles["roll"] >= threshold and reverse == False) or (angles["roll"] <= -threshold and reverse == True):
            mapper.switch_left()
            last_switch_time = current_time
            led[0]=(0, 255, 0)
        elif (angles["roll"] <= -threshold and reverse == False) or (angles["roll"] >= threshold and reverse == True):
            mapper.switch_right()
            last_switch_time = current_time
            led[0]=(255, 0, 0)
    else:
        led[0]=(0,0,0)
    led.write()
    return last_switch_time


def initialize():
    imu.set_output_types(["angles"])
    imu.save_settings()
    # Flex sensor calibration is handled in FlexSensorMapper.__init__


def main():
    last_switch_time = 0  # Initialize the time of the last switch
    while True:
        primary_top = ""
        primary_bottom = ""
        footer = ""
        
        imu.update()
        angles = imu.get_angles()
        
        # Get triggered notes from the mapper
        triggered_notes, detriggered_notes, active_notes = mapper.read(verbose=False)
        for note in triggered_notes:
            midi.note_on(NOTE[note])
        for note in detriggered_notes:
            midi.note_off(NOTE[note])
        for note in active_notes:
            primary_top += (note + " ")
        
        for note in mapper.get_key_mappings():
            primary_bottom += (note + " ")
        
        if angles:
            footer = str(angles['roll'])
            print(footer)
            last_switch_time = handle_imu_switching(angles, last_switch_time, mapper, reverse=True)
        
        disp.clear()
        disp.draw_header(footer)
        disp.draw_primary(primary_top, primary_bottom)
        disp.update()
        
        time.sleep(0.05)

if __name__ == '__main__':
    initialize()
    main()