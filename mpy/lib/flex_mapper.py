from lib import flexsensor


# import button_flex as flexsensor

class FlexSensorMapper:
    """
    FlexSensorMapper class to map flex sensor readings to piano notes.

    This class initializes flex sensors, calibrates them, and provides methods to read sensor states,
    detect triggered, detriggered, and active notes, and switch the note mappings across a range of piano keys.
    """

    def __init__(self, sensor_pins: list = [5, 4, 3, 2, 1], thresholds: tuple = (60, 60, 60, 60, 60)):
        """
        Initializes the FlexSensorMapper.

        Sets up flex sensors with specific ADC channels, assigns hardcoded thresholds, defines lists of
        white and black piano keys from octave 3 to 5, sets the initial mapping to white keys C4 through G4,
        initializes state tracking, and calibrates each sensor.

        Args:
            sensor_pins (list): List of ints for defining flex sensors.
            thresholds (tuple):
        """
        # Initialize flex sensors with specific ADC channels for buttons
        self.flex_sensors = [flexsensor.FlexSensor(i) for i in sensor_pins]  # For buttons
        # Thresholds for each sensor
        self.thresholds = thresholds
        # Define the white keys of the piano from C3 to B5 (three octaves)
        self.white_notes = [note + str(octave) for octave in range(3, 6) for note in
                            ['C', 'D', 'E', 'F', 'G', 'A', 'B']]
        # Define the black keys of the piano from C#3 to A#5 (three octaves)
        self.black_notes = [note + str(octave) for octave in range(3, 6) for note in ['C#', 'D#', 'F#', 'G#', 'A#']]
        # Start with white keys
        self.current_notes = self.white_notes
        # Start with mapping to C4, D4, E4, F4, G4 (index 7 corresponds to 'C4')
        self.start_index = 7
        # Initialize previous values to track state changes
        self.previous_values = [False] * 5
        # Calibrate each flex sensor upon initialization
        for fs in self.flex_sensors:
            fs.calibrate()

    def get_key_mappings(self):
        """
        Get current key mappings

        Returns:
            list: The current key mappings (five notes) after attempting to switch.
        """
        # Return the current mappings
        return self.current_notes[self.start_index: self.start_index + 5]

    def read(self, verbose: bool = False):
        """
        Reads the current state of the flex sensors and detects triggered, detriggered, and active notes.

        Args:
            verbose (bool): If True, prints the triggered and detriggered notes for debugging.

        Returns:
            tuple: (triggered_notes, detriggered_notes, active_notes), where each is a list of note strings.
                   - triggered_notes: Notes that transitioned from off to on.
                   - detriggered_notes: Notes that transitioned from on to off.
                   - active_notes: Notes that are currently on based on the latest sensor readings.
        """
        # Read current flex sensor values and compare with thresholds
        current_values = [fs.read() >= threshold for fs, threshold in zip(self.flex_sensors, self.thresholds)]
        triggered_notes = []
        detriggered_notes = []

        # Check for state transitions
        for i in range(5):
            if current_values[i] and not self.previous_values[i]:
                # Triggered: False to True transition
                note = self.current_notes[self.start_index + i]
                triggered_notes.append(note)
            elif not current_values[i] and self.previous_values[i]:
                # Detriggered: True to False transition
                note = self.current_notes[self.start_index + i]
                detriggered_notes.append(note)

        # Update previous values to current values for the next read
        self.previous_values = current_values[:]

        # Determine currently active notes based on the latest sensor readings
        active_notes = [self.current_notes[self.start_index + i] for i in range(5) if current_values[i]]

        # Print state changes if verbose mode is enabled
        if verbose:
            print(current_values)
            # print(f"Triggered: {triggered_notes}, Detriggered: {detriggered_notes}")

        return triggered_notes, detriggered_notes, active_notes

    def switch_left(self):
        """
        Shifts the note mapping to the left by one white key, staying within bounds.

        Returns:
            list: The current key mappings (five notes) after attempting to switch.
        """
        # Shift left by one, but not below index 0
        self.start_index = max(0, self.start_index - 2)
        # Return the current mappings
        return self.get_key_mappings()

    def switch_right(self):
        """
        Shifts the note mapping to the right by one white key, staying within bounds.

        Returns:
            list: The current key mappings (five notes) after attempting to switch.
        """
        # Shift right by one, but not beyond the end of the note list
        self.start_index = min(len(self.current_notes) - 5, self.start_index + 2)
        # Return the current mappings
        return self.get_key_mappings()

    def toggle_black_white(self):
        """
        Toggles between mapping to white keys and black keys, resetting the start index to an appropriate
        value for the selected mode (7 for white, 5 for black).

        Returns:
            list: The current key mappings (five notes) after toggling.
        """
        if self.current_notes is self.white_notes:
            self.current_notes = self.black_notes
            self.start_index = 5  # Start at C#4 to A#4 for black keys
        else:
            self.current_notes = self.white_notes
            self.start_index = 7  # Start at C4 to G4 for white keys
        return self.get_key_mappings()

