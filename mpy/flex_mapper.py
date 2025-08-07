#import flexsensor
import button_flex as flexsensor

class FlexSensorMapper:
    def __init__(self):
        # Initialize flex sensors with the same ADC channels as in the original code
        #self.flex_sensors = [flexsensor.flexSensor(i) for i in [0, 1, 3, 4, 5]]
        self.flex_sensors = [flexsensor.flexSensor(i) for i in [0, 1, 2, 5, 8]] #for buttons
        # Hardcode thresholds as in the original code
        #self.thresholds = (1000, 1000, 1000, 1000, 1000)
        self.thresholds = (0.5, 0.5, 0.5, 0.5, 0.5) #for buttons
        # Define the white keys of the piano from C3 to B5 (covering three octaves)
        self.note_list = [note + str(octave) for octave in range(3, 6) for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']]
        # Start with mapping to C4, D4, E4, F4, G4 (index 7 corresponds to 'C4')
        self.start_index = 7
        # Initialize previous values to track state changes
        self.previous_values = [False] * 5
        # Calibrate flex sensors upon initialization, as in the original code
        for fs in self.flex_sensors:
            fs.calibrate()

    def read(self, verbose:bool=False):
        # Read current flex sensor values and compare with thresholds
        current_values = [fs.read() >= threshold for fs, threshold in zip(self.flex_sensors, self.thresholds)]
        triggered_notes = []
        # Check for new triggers (False to True transitions)
        for i in range(5):
            if current_values[i] and not self.previous_values[i]:
                # Map the flex sensor index to the current note based on start_index
                note = self.note_list[self.start_index + i]
                triggered_notes.append(note)
        # Update previous values
        self.previous_values = current_values[:]
        if verbose:
            print(triggered_notes)
        return triggered_notes

    def switch_left(self):
        # Shift the mapping left by one white key if not at the start
        if self.start_index > 0:
            self.start_index -= 1

    def switch_right(self):
        # Shift the mapping right by one white key if not at the end
        if self.start_index + 5 < len(self.note_list):
            self.start_index += 1