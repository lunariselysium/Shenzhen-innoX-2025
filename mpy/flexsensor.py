from machine import ADC, Pin
from time import sleep


class FlexSensor:
    """
    A class to interface with a flex sensor using ADC on a microcontroller.

    This class reads values from a flex sensor connected to an ADC pin,
    calibrates a zero value, and optionally applies an exponential moving
    average filter to smooth noisy readings.

    Attributes:
        ADC (machine.ADC): The ADC object for reading sensor values.
        zeroValue (int): The calibrated zero value of the sensor.
        value (int): The raw absolute difference from the zero value.
        filtered_value (float): The filtered sensor value (if filtering is enabled).
        use_filter (bool): Flag to enable or disable filtering.
        alpha (float): Smoothing factor for the exponential moving average filter.
    """

    def __init__(self, io_pin: int, use_filter: bool = True, alpha: float = 0.2):
        """
        Initializes the flexSensor instance.

        Args:
            io_pin (int): The GPIO pin number connected to the flex sensor.
            use_filter (bool, optional): Enable filtering of sensor readings. Defaults to True.
            alpha (float, optional): Smoothing factor for the filter (0 < alpha <= 1).
                Smaller values provide more smoothing. Defaults to 0.2.
        """
        self.ADC = ADC(Pin(io_pin))
        self.ADC.atten(ADC.ATTN_11DB)
        self.zeroValue = 1100
        self.value = 0  # Raw absolute difference
        self.filtered_value = 0  # Filtered value
        self.use_filter = use_filter
        self.alpha = alpha  # Smoothing factor for exponential moving average (0 < alpha <= 1, smaller alpha = more smoothing)

    def calibrate(self, time_range: int = 5, ms_interval: int = 100):
        """
        Calibrates the zero value of the sensor by averaging readings over a period.

        Args:
            time_range (int, optional): Number of readings to take for calibration. Defaults to 5.
            ms_interval (int, optional): Interval in milliseconds between readings. Defaults to 100.
        """
        readings = []
        for i in range(time_range):
            readings.append(self.ADC.read())
            sleep(ms_interval / 1000)
        self.zeroValue = int(sum(readings) / len(readings))
        self.filtered_value = 0  # Reset filtered value after calibration

    def read(self):
        """
        Reads the current sensor value, applies filtering if enabled, and returns the result.

        Returns:
            float or int: The filtered value if filtering is enabled, otherwise the raw absolute difference.
        """
        raw_value = self.ADC.read()
        self.value = abs(self.zeroValue - raw_value)

        if self.use_filter:
            # Apply exponential moving average filter
            self.filtered_value = self.alpha * self.value + (1 - self.alpha) * self.filtered_value
            return self.filtered_value
        else:
            return self.value


if __name__ == "__main__":
    fs = FlexSensor(2)
    fs.calibrate()
    while True:
        print(fs.read())
        sleep(0.1)