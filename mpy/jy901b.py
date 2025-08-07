import machine
import time

class JY901B:
    """
    A MicroPython library class for the JY901B 10-axis IMU module connected via UART.
    Provides methods to configure the IMU, read sensor data, and perform calibration.
    """

    def __init__(self, uart=None, uart_id=0, baudrate=9600, tx_pin=0, rx_pin=1):
        """
        Initialize the JY901B IMU with UART settings.

        Args:
            uart_id (int): UART ID (default: 0)
            baudrate (int): Baud rate (default: 9600)
            tx_pin (int): TX pin number (default: 0)
            rx_pin (int): RX pin number (default: 1)
        """
        if uart:
            self.uart = uart
        else:
            self.uart = machine.UART(uart_id, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))
        # Initialize internal storage for sensor data
        self.angles = None
        self.acceleration = None
        self.angular_velocity = None
        self.magnetic_field = None
        self.time_data = None
        # Add more data types as needed in the future
        self.unlock()  # Unlock IMU for configuration

    def send_command(self, cmd):
        """
        Send a command to the IMU.

        Args:
            cmd (list): List of bytes to send
        """
        self.uart.write(bytes(cmd))

    def unlock(self):
        """Unlock the IMU for configuration commands."""
        self.send_command([0xFF, 0xAA, 0x69, 0x88, 0xB5])
        time.sleep(0.1)

    def set_output_types(self, types):
        """
        Configure which data types the IMU should output continuously.

        Args:
            types (list): List of strings specifying output types, e.g., ["angles", "acceleration"]
        """
        rsw = 0
        type_bits = {
            "time": 0,
            "acceleration": 1,
            "angular_velocity": 2,
            "angles": 3,
            "magnetic_field": 4,
            "port_status": 5,
            "pressure_height": 6,
            "longitude_latitude": 7,
            "gps_data": 8,
            "quaternion": 9,
            "gps_accuracy": 10,
        }
        for t in types:
            if t in type_bits:
                rsw |= (1 << type_bits[t])
        self.unlock()
        self.send_command([0xFF, 0xAA, 0x02, rsw & 0xFF, (rsw >> 8) & 0xFF])

    def save_settings(self):
        """Save the current IMU settings to persist after power-off."""
        self.send_command([0xFF, 0xAA, 0x00, 0x00, 0x00])

    def calibrate_accelerometer(self):
        """Calibrate the accelerometer. Ensure the IMU is stationary during calibration."""
        self.unlock()
        self.send_command([0xFF, 0xAA, 0x01, 0x01, 0x00])  # Enter calibration mode
        time.sleep(1)
        self.send_command([0xFF, 0xAA, 0x01, 0x00, 0x00])  # Exit calibration mode

    def read_packet(self):
        """
        Read and validate a data packet from the IMU.

        Returns:
            tuple: (packet_type, packet_data) or (None, None) if invalid/no data
        """
        if self.uart.any() >= 11:
            data = self.uart.read(11)
            if data and len(data) == 11 and data[0] == 0x55:
                packet_type = data[1]
                packet_data = data[2:10]
                checksum = data[10]
                calculated_checksum = sum(data[0:10]) & 0xFF
                if checksum == calculated_checksum:
                    return packet_type, packet_data
        return None, None

    def update(self):
        """
        Process all available data packets from the UART buffer and update internal state.
        Call this method periodically to refresh sensor data.
        """
        while self.uart.any() >= 11:
            packet_type, packet_data = self.read_packet()
            if packet_type == 0x50:
                self.time_data = self.parse_time(packet_data)
            elif packet_type == 0x51:
                self.acceleration = self.parse_acceleration(packet_data)
            elif packet_type == 0x52:
                self.angular_velocity = self.parse_angular_velocity(packet_data)
            elif packet_type == 0x53:
                self.angles = self.parse_angles(packet_data)
            elif packet_type == 0x54:
                self.magnetic_field = self.parse_magnetic_field(packet_data)
            # Add more packet types as needed

    def _to_signed_short(self, low, high):
        """
        Convert two bytes to a signed 16-bit integer.

        Args:
            low (int): Low byte
            high (int): High byte

        Returns:
            int: Signed 16-bit value
        """
        value = (high << 8) | low
        if value & 0x8000:
            value -= 65536
        return value

    def parse_time(self, data):
        """
        Parse time data packet.

        Returns:
            dict: Time components
        """
        year = data[0]
        month = data[1]
        day = data[2]
        hour = data[3]
        minute = data[4]
        second = data[5]
        millisecond = (data[6] | (data[7] << 8))
        return {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "millisecond": millisecond
        }

    def parse_acceleration(self, data):
        """
        Parse acceleration data packet.

        Returns:
            dict: Acceleration in m/s² (ax, ay, az)
        """
        ax = self._to_signed_short(data[0], data[1]) / 32768.0 * 16 * 9.8
        ay = self._to_signed_short(data[2], data[3]) / 32768.0 * 16 * 9.8
        az = self._to_signed_short(data[4], data[5]) / 32768.0 * 16 * 9.8
        return {"ax": ax, "ay": ay, "az": az}

    def parse_angular_velocity(self, data):
        """
        Parse angular velocity data packet.

        Returns:
            dict: Angular velocity in °/s (gx, gy, gz)
        """
        gx = self._to_signed_short(data[0], data[1]) / 32768.0 * 2000
        gy = self._to_signed_short(data[2], data[3]) / 32768.0 * 2000
        gz = self._to_signed_short(data[4], data[5]) / 32768.0 * 2000
        return {"gx": gx, "gy": gy, "gz": gz}

    def parse_angles(self, data):
        """
        Parse angle data packet.

        Returns:
            dict: Angles in degrees (roll, pitch, yaw)
        """
        roll = self._to_signed_short(data[0], data[1]) / 32768.0 * 180.0
        pitch = self._to_signed_short(data[2], data[3]) / 32768.0 * 180.0
        yaw = self._to_signed_short(data[4], data[5]) / 32768.0 * 180.0
        return {"roll": roll, "pitch": pitch, "yaw": yaw}

    def parse_magnetic_field(self, data):
        """
        Parse magnetic field data packet.

        Returns:
            dict: Magnetic field in raw units (hx, hy, hz)
        """
        hx = self._to_signed_short(data[0], data[1])
        hy = self._to_signed_short(data[2], data[3])
        hz = self._to_signed_short(data[4], data[5])
        return {"hx": hx, "hy": hy, "hz": hz}

    # Getter methods for accessing the latest sensor data
    def get_time(self):
        """Get the latest time data."""
        return self.time_data

    def get_acceleration(self):
        """Get the latest acceleration data."""
        return self.acceleration

    def get_angular_velocity(self):
        """Get the latest angular velocity data."""
        return self.angular_velocity

    def get_angles(self):
        """Get the latest angle data."""
        return self.angles

    def get_magnetic_field(self):
        """Get the latest magnetic field data."""
        return self.magnetic_field