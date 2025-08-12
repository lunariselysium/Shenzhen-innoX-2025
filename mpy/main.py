import time
from machine import Pin, I2C
from random import choice
import bluetooth
import neopixel
from lib.jy901b import JY901B
from lib.ble_midi_instrument import BLEMidi, NOTE
from lib.flex_mapper import FlexSensorMapper
from lib.display_manager import DisplayManager
from lib.light_manager import LightManager
from lib.animations import WipeAnimation

i2c = I2C(0, sda=Pin(11), scl=Pin(10))
ble = bluetooth.BLE()

led = neopixel.NeoPixel(Pin(38, Pin.OUT), 1)
imu = JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=8)
midi = BLEMidi(ble, name="MIDIMitts")
mapper = FlexSensorMapper(sensor_pins=[5, 4, 3, 2, 1], thresholds=(20, 25, 35, 30, 38))
disp = DisplayManager(i2c)
lm = LightManager(Pin(9, Pin.OUT), total_count = 25, segment_count = 5)

palette  = [
    (100,0,0),
    (0,100,0),
    (0,0,100),
    (255, 99, 71),  # tomato red
    (135, 206, 235),  # sky blue
    (255, 215, 0),  # gold
    (60, 179, 113),  # medium sea green
]



def handle_imu_switching(angles, accel, last_switch_time, mapper, cooldown_ms=500, threshold_roll=30, threshold_accel=10, reverse: bool = False):
    """Handle IMU-based switching based on pitch angle, with a set cooldown. Left/right can be reversed"""
    current_time = time.ticks_ms()

    if current_time - last_switch_time >= cooldown_ms:
        if (angles["roll"] >= threshold_roll and reverse == False) or (angles["roll"] <= -threshold_roll and reverse == True):
            mapper.switch_left()
            last_switch_time = current_time
            led[0] = (0, 255, 0)
        elif (angles["roll"] <= -threshold_roll and reverse == False) or (angles["roll"] >= threshold_roll and reverse == True):
            mapper.switch_right()
            last_switch_time = current_time
            led[0] = (255, 0, 0)
        elif abs(accel["az"]-9.8) >= threshold_accel:
            mapper.toggle_black_white()
    else:
        led[0] = (0, 0, 0)
    led.write()
    return last_switch_time


def initialize():
    imu.set_output_types(["angles","acceleration"])
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
        accel = imu.get_acceleration()

        # Get triggered notes from the mapper
        triggered_notes, detriggered_notes, active_notes = mapper.read(verbose=False)
        for note in triggered_notes:
            midi.note_on(NOTE[note])
            try:
                lm.add_animation(
                    WipeAnimation(lm.get_segment_start(mapper.get_key_mappings().index(note)),lm.segment_length,800,choice(palette),)
                )
            except ValueError:
                pass

        for note in detriggered_notes:
            midi.note_off(NOTE[note])
            try:
                lm.add_animation(
                    WipeAnimation(lm.get_segment_start(mapper.get_key_mappings().index(note)),lm.segment_length, 800, (0,0,0),)
                )
            except ValueError:
                pass

        for note in active_notes:
            primary_top += (note + " ")

        for note in mapper.get_key_mappings():
            primary_bottom += (note + " ")

        if angles and accel:
            footer = str(angles['roll'])
            #print(footer)
            last_switch_time = handle_imu_switching(angles, accel, last_switch_time, mapper, reverse=True)

        disp.clear()
        disp.draw_header(footer)
        disp.draw_primary(primary_top, primary_bottom)
        disp.update()

        lm.update()

        time.sleep(0.05)


if __name__ == '__main__':
    initialize()
    main()
