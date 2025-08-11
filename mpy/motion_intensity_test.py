import time
import math
from lib import jy901b
import bluetooth
from lib.ble_midi_instrument import BLEMidi

ble = bluetooth.BLE()
imu = jy901b.JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=8)
midi = BLEMidi(ble, name="MIDIMitts")

imu.set_output_types(["acceleration", "angular_velocity"])
imu.save_settings()

# ---- CONFIGURATION ----
MIDI_CC_NUMBER = 7      # e.g., Mod Wheel
MIDI_CHANNEL   = 0      # 0–15
ALPHA          = 0.7    # weight for gyro
BETA           = 0.3    # weight for accel magnitude
SMOOTH_FACTOR  = 0.2    # exponential smoothing

# ---- HELPERS ----
def magnitude(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

# ---- STATE ----
smoothed_intensity = 0

# ---- LOOP ----
while True:
    imu.update()
    # Get raw IMU data (replace with your IMU method calls)
    accel = imu.get_acceleration()   # m/s²
    gyro = imu.get_angular_velocity()    # °/s

    # Pick main bowing axis from gyro (replace 'gx' with your axis)
    gyro_val = abs(gyro['gx'])  # main rotational speed

    # Accel magnitude minus gravity
    accel_mag = magnitude((accel['ax'], accel['ay'], accel['az']))
    accel_val = abs(accel_mag - 9.81)  # remove gravity

    # Hybrid motion intensity
    motion_intensity = ALPHA * gyro_val + BETA * accel_val

    # Map to MIDI CC range
    # Here you might scale — tweak 'scale_factor'
    scale_factor = 1.0  # adjust until full range is reached
    cc_value = motion_intensity * scale_factor

    # Smooth for stability
    smoothed_intensity = (
        SMOOTH_FACTOR * cc_value + (1 - SMOOTH_FACTOR) * smoothed_intensity
    )

    # Send MIDI CC
    print(smoothed_intensity)

    time.sleep(0.01)  # 100 Hz loop