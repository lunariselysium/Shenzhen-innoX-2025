import time
from machine import Pin, I2C
from random import choice
import bluetooth
import neopixel
from lib.jy901b import JY901B
from lib.ble_midi_instrument import BLEMidi, NOTE
from lib.flex_mapper import FlexSensorMapper
from lib.fake_flex_mapper import FakeFlexSensorMapper
from internationale import the_internationale
from lib.display_manager import DisplayManager
from lib.light_manager import LightManager
from lib.animations import WipeAnimation, ColorTransitionAnimation

Pin(13,Pin.OUT).value(1)
Pin(14,Pin.OUT).value(0)
fake_control_pin = Pin(12,Pin.IN, Pin.PULL_DOWN)
if fake_control_pin.value():
    fake_on = True
else:
    fake_on = False

i2c = I2C(0, sda=Pin(11), scl=Pin(10))
ble = bluetooth.BLE()

led = neopixel.NeoPixel(Pin(38, Pin.OUT), 1)
imu = JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=8)
midi = BLEMidi(ble, name="MIDIMitts")
if not fake_on:
    #mapper = FlexSensorMapper(sensor_pins=[5, 4, 3, 2, 1], thresholds=(20, 25, 35, 30, 38)) # left
    mapper = FlexSensorMapper(sensor_pins=[1, 2, 3, 4, 5], thresholds=(20, 35, 30, 35, 35)) # right
    #mapper = FlexSensorMapper(sensor_pins=[5, 4, 3, 2, 1], thresholds=(0.5,0.5,0.5,0.5,0.5))
else:
    mapper = FakeFlexSensorMapper()
ode_to_joy = [
        ('E4', 800), ('E4', 800), ('F4', 800), ('G4', 800),
        ('G4', 800), ('F4', 800), ('E4', 800), ('D4', 800),
        ('C4', 800), ('C4', 800), ('D4', 800), ('E4', 800),
        ('E4', 600), ('D4', 200), ('D4', 1000), ('REST', 400),
        ('E4', 800), ('E4', 800), ('F4', 800), ('G4', 800),
        ('G4', 800), ('F4', 800), ('E4', 800), ('D4', 800),
        ('C4', 800), ('C4', 800), ('D4', 800), ('E4', 800),
        ('D4', 600), ('C4', 200), ('C4', 1000),
    ]
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



def handle_imu_switching(angles, accel, last_switch_time, mapper, cooldown_ms=500, threshold_pitch=30, threshold_accel=5, reverse: bool = False):
    """Handle IMU-based switching based on pitch angle, with a set cooldown. Left/right can be reversed"""
    current_time = time.ticks_ms()

    if current_time - last_switch_time >= cooldown_ms:
        if (angles["pitch"] >= threshold_pitch and reverse == False) or (angles["pitch"] <= -threshold_pitch and reverse == True):
            mapper.switch_left()
            last_switch_time = current_time
            led[0] = (0, 255, 0)
        elif (angles["pitch"] <= -threshold_pitch and reverse == False) or (angles["pitch"] >= threshold_pitch and reverse == True):
            mapper.switch_right()
            last_switch_time = current_time
            led[0] = (255, 0, 0)
        elif abs(accel["az"]-9.8) >= threshold_accel:
            mapper.toggle_black_white()
            last_switch_time = current_time
            led[0] = (0, 0, 255)

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
    has_started = False
    while True:
        if fake_on and (not has_started) and (not fake_control_pin.value()):
            has_started = True
            print("start in 5 seconds")
            mapper.start(the_internationale, 5)
            led[0]=(255,255,255)
            led.write()
            continue
        else:
            led[0]=(0,0,0)
        primary_top = ""
        primary_bottom = ""
        footer = ""

        imu.update()
        angles = imu.get_angles()
        accel = imu.get_acceleration()

        # Get triggered notes from the mapper
        if fake_on:
            triggered_notes, detriggered_notes, active_notes, switch_action = mapper.read(verbose=False)
        else:
            triggered_notes, detriggered_notes, active_notes = mapper.read(verbose=False)
            switch_action=0

        if switch_action == 1:  # Switched Right
            print("Switched Right!")
            led[0] = (255, 0, 0)
            led.write()
        elif switch_action == -1:  # Switched Left
            print("Switched Left!")
            led[0] = (0, 255, 0)
            led.write()
        elif switch_action == 2:  # Toggled Black/White
            print("Toggled Black/White!")
            led[0] = (0, 0, 255)
            led.write()
        else:
            # Turn LED off if no switch happened
            led[0] = (0, 0, 0)
            led.write()

        for note in triggered_notes:
            midi.note_on(NOTE[note])
            try:
                lm.add_animation(
                    WipeAnimation(lm.get_segment_start(4-mapper.get_key_mappings().index(note)),lm.segment_length,400,choice(palette),)
                )
            except ValueError:
                pass

        for note in detriggered_notes:
            midi.note_off(NOTE[note])
            try:
                lm.add_animation(
                    ColorTransitionAnimation(lm.get_segment_start(4-mapper.get_key_mappings().index(note)),lm.segment_length, 400, (0,0,0),)
                )
            except ValueError:
                pass

        # for note in active_notes:
            # primary_top += (note + " ")

        for note in mapper.get_key_mappings():
            if note in active_notes:
                primary_top += "1 "
            else:
                primary_top += "0 "
            primary_bottom += (note + " ")

        if angles and accel:
            footer = str(angles['pitch'])
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
