import time
from machine import Pin, I2C, UART
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


def draw_frame(display, primary_text: list, secondary_text: str):
    display.fill_rect(0, 0, 128, 16, 1)
    display.text(secondary_text, 0, 0, 0)
    display.text(primary_text[0], 0, 16, 1)
    display.text(str(primary_text[1]), 0, 32, 1)

def initialize():
    display.poweron()
    display.contrast(255)
    display.fill(0)
    imu.set_output_types(["angles"])
    imu.save_settings()
    # Flex sensor calibration is now handled in FlexSensorMapper.__init__

def handle_imu_switching(angles, last_switch_time, mapper, cooldown_s=2, threshold=45, reverse:bool=False):
    """Handle IMU-based switching based on pitch angle, with a set cooldown. Left/right can be reversed"""
    current_time = time.time()
    if current_time - last_switch_time >= cooldown_s:
        if (angles["pitch"] >= threshold and reverse == False) or (angles["pitch"] <= -threshold and reverse == True):
            mapper.switch_left()
            last_switch_time = current_time
        elif (angles["pitch"] <= -threshold and reverse == False) or (angles["pitch"] >= threshold and reverse == True):
            mapper.switch_right()
            last_switch_time = current_time
    return last_switch_time

def main():
    last_switch_time = 0  # Initialize the time of the last switch
    while True:
        primary_text = ["",""]
        secondary_text = ""
        
        display.fill(0)
        imu.update()
        angles = imu.get_angles()
        
        # Get triggered notes from the mapper
        triggered_notes, detriggered_notes, active_notes = mapper.read(verbose=False)
        for note in triggered_notes:
            midi.note_on(NOTE[note])
        for note in detriggered_notes:
            midi.note_off(NOTE[note])
        for note in active_notes:
            primary_text[0] += (note + " ")
        
        for note in mapper.get_key_mappings():
            primary_text[1] += (note + " ")
        
        if angles:
            secondary_text = str(angles['pitch'])
            last_switch_time = handle_imu_switching(angles, last_switch_time, mapper)
        
        draw_frame(display, primary_text, secondary_text)
        try:
            display.show()
        except BaseException as e:
            print(e)
        
        time.sleep(0.05)

if __name__ == '__main__':
    initialize()
    main()