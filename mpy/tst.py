import time

import bluetooth
from machine import Pin, I2C

import jy901b
import ssd1306
from ble_midi_instrument import BLEMidi, NOTE
from flex_mapper import FlexSensorMapper

i2c = I2C(0, sda=Pin(21), scl=Pin(20))
ble = bluetooth.BLE()

display = ssd1306.SSD1306_I2C(128, 64, i2c)
imu = jy901b.JY901B(uart_id=1, baudrate=9600, tx_pin=7, rx_pin=6)
midi = BLEMidi(ble, name="MIDIMitts")
mapper = FlexSensorMapper()


def handle_imu_switching(angles, last_switch_time, mapper, cooldown_s=2, threshold=45, reverse: bool = False):
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


def draw_frame(display, imu_data, active_notes, key_mappings):
    """Draw the display frame with IMU data and note information"""
    display.fill(0)

    # 显示加速度数据
    if imu_data['acceleration']:
        accel = imu_data['acceleration']
        display.text(f"A:{accel['ax']:.1f},{accel['ay']:.1f},{accel['az']:.1f}", 0, 0)
    else:
        display.text("A: No data", 0, 0)

    # 显示角速度数据
    if imu_data['angular_velocity']:
        gyro = imu_data['angular_velocity']
        display.text(f"G:{gyro['gx']:.1f},{gyro['gy']:.1f},{gyro['gz']:.1f}", 0, 10)
    else:
        display.text("G: No data", 0, 10)

    # 显示角度数据
    if imu_data['angles']:
        angles = imu_data['angles']
        display.text(f"P:{angles['pitch']:.1f} R:{angles['roll']:.1f} Y:{angles['yaw']:.1f}", 0, 20)
    else:
        display.text("Angles: No data", 0, 20)

    # 显示磁场数据
    if imu_data['magnetic_field']:
        mag = imu_data['magnetic_field']
        display.text(f"M:{mag['hx']:.1f},{mag['hy']:.1f},{mag['hz']:.1f}", 0, 30)
    else:
        display.text("M: No data", 0, 30)

    # 显示音符信息
    display.text(f"Trig:{' '.join(active_notes)}", 0, 40)
    display.text(f"Map:{' '.join(key_mappings)}", 0, 50)


def initialize():
    """Initialize the system components"""
    display.poweron()
    display.contrast(255)
    display.fill(0)
    display.text("Initializing...", 0, 0)
    display.show()

    # 设置IMU输出所有数据类型
    imu.set_output_types(["acceleration", "angular_velocity", "angles", "magnetic_field"])
    imu.save_settings()
    time.sleep(1)

    # Flex sensor calibration is now handled in FlexSensorMapper.__init__
    display.fill(0)
    display.text("Ready!", 0, 0)
    display.show()
    time.sleep(0.5)


def main():
    """Main program loop"""
    last_switch_time = 0
    active_notes = []  # Initialize active_notes as empty list
    key_mappings = []  # Initialize key_mappings as empty list

    while True:
        # 获取传感器数据
        imu.update()

        # 组织IMU数据结构
        imu_data = {
            'acceleration': imu.get_acceleration(),
            'angular_velocity': imu.get_angular_velocity(),
            'angles': imu.get_angles(),
            'magnetic_field': imu.get_magnetic_field()
        }

        # 获取音符信息
        triggered_notes, detriggered_notes, new_active_notes = mapper.read(verbose=False)
        active_notes = new_active_notes  # Update active_notes
        key_mappings = mapper.get_key_mappings()

        # 发送MIDI音符
        for note in triggered_notes:
            midi.note_on(NOTE[note])
        for note in detriggered_notes:
            midi.note_off(NOTE[note])

        # 处理IMU切换
        if imu_data['angles']:
            angles = imu_data['angles']
            last_switch_time = handle_imu_switching(angles, last_switch_time, mapper)

        # 绘制界面
        draw_frame(display, imu_data, active_notes, key_mappings)

        try:
            display.show()
        except Exception as e:
            print(f"Display error: {e}")

        time.sleep(0.05)


if __name__ == '__main__':
    initialize()
    main()
