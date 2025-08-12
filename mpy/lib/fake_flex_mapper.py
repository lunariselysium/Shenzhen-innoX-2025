import time


class FakeFlexSensorMapper:
    """
    A fake FlexSensorMapper to simulate playing a song for testing purposes.

    This class mimics the behavior of the real FlexSensorMapper, generating
    note events based on a pre-defined song. It automatically handles
    switching hand positions (mappings) and reports these switches.
    """

    def __init__(self, sensor_pins: list = [1, 2, 3, 4, 5], thresholds: tuple = (20, 35, 30, 35, 35)):
        """
        Initializes the FakeFlexSensorMapper in a stopped state.
        """
        self.white_notes = [note + str(octave) for octave in range(3, 6) for note in
                            ['C', 'D', 'E', 'F', 'G', 'A', 'B']]
        self.black_notes = [note + str(octave) for octave in range(3, 6) for note in ['C#', 'D#', 'F#', 'G#', 'A#']]
        self.current_notes = self.white_notes
        self.start_index = 7  # Default start at C4

        self.song = []
        self.song_index = 0
        self.next_event_time = 0
        self.note_state = 'OFF'
        self.currently_playing_note = None
        self.start_time = 0
        self.last_switch_action = 0  # 0:None, -1:Left, 1:Right, 2:Toggle B/W

    def start(self, song: list, delay_s: int = 2):
        """
        Starts playing a new song after a specified delay.
        """
        self.song = song
        self.song_index = 0
        self.note_state = 'OFF'
        self.currently_playing_note = None
        self.last_switch_action = 0
        self.start_time = time.ticks_add(time.ticks_ms(), delay_s * 1000)
        self.next_event_time = self.start_time

    def get_key_mappings(self):
        """Returns the current five notes that are mapped."""
        return self.current_notes[self.start_index: self.start_index + 5]

    def read(self, verbose: bool = False):
        """
        Generates note events to play the loaded song and reports mapping switches.

        Returns:
            tuple: (triggered_notes, detriggered_notes, active_notes, switch_indicator)
                   - switch_indicator: -1 (left), 0 (none), 1 (right), 2 (toggled b/w)
        """
        current_time = time.ticks_ms()

        # Consume the last switch action and reset it for the current cycle
        switch_indicator = self.last_switch_action
        self.last_switch_action = 0

        if not self.song or self.song_index >= len(self.song) or time.ticks_diff(self.start_time, current_time) > 0:
            return [], [], [], switch_indicator

        triggered_notes = []
        detriggered_notes = []
        active_notes = []

        if time.ticks_diff(self.next_event_time, current_time) > 0:
            if self.note_state == 'ON' and self.currently_playing_note:
                active_notes.append(self.currently_playing_note)
            return [], [], active_notes, switch_indicator

        if self.note_state == 'OFF':
            if self.song_index >= len(self.song):
                return [], [], [], switch_indicator

            note_to_play, duration = self.song[self.song_index]

            if note_to_play == "REST":
                self.next_event_time = time.ticks_add(current_time, duration)
                self.song_index += 1
                return [], [], [], switch_indicator

            if note_to_play not in self.get_key_mappings():
                # Note is out of range, perform a switch and wait for the next cycle
                self._switch_to_note(note_to_play)
                self.next_event_time = time.ticks_add(current_time, 100)  # Pause for switch
                return [], [], [], self.last_switch_action  # Return immediately with switch info
            else:
                # Note is in range, trigger it
                triggered_notes.append(note_to_play)
                self.currently_playing_note = note_to_play
                self.note_state = 'ON'
                self.next_event_time = time.ticks_add(current_time, duration)

        elif self.note_state == 'ON':
            if self.currently_playing_note:
                detriggered_notes.append(self.currently_playing_note)
            self.currently_playing_note = None
            self.note_state = 'OFF'
            self.song_index += 1
            self.next_event_time = time.ticks_add(current_time, 50)  # Small gap between notes

        if self.note_state == 'ON' and self.currently_playing_note:
            active_notes.append(self.currently_playing_note)

        return triggered_notes, detriggered_notes, active_notes, switch_indicator

    def _switch_to_note(self, note):
        """
        Calculates the most efficient switch (left, right, or toggle) to bring
        the target note into the mapping and sets the `last_switch_action` flag.
        The goal is to re-center the mapping around the new note to minimize
        future switches.
        """
        is_black_note = '#' in note
        old_start_index = self.start_index
        old_notes_type = self.current_notes

        # 1. Determine if a black/white toggle is needed
        if (is_black_note and self.current_notes is self.white_notes) or \
                (not is_black_note and self.current_notes is self.black_notes):
            self.current_notes = self.black_notes if is_black_note else self.white_notes
            self.last_switch_action = 2

        # 2. Find the note's index in the correct list
        try:
            note_index = self.current_notes.index(note)
        except ValueError:
            # Note doesn't exist in our defined piano range, skip it
            self.song_index += 1
            return

        # 3. Calculate new start_index to center the note (index - 2)
        new_start_index = max(0, min(note_index - 2, len(self.current_notes) - 5))
        self.start_index = new_start_index

        # 4. Determine switch direction if we didn't just toggle
        if self.last_switch_action != 2 and old_notes_type is self.current_notes:
            if new_start_index < old_start_index:
                self.last_switch_action = -1  # Switched Left
            elif new_start_index > old_start_index:
                self.last_switch_action = 1  # Switched Right

    # These methods are not needed for the fake mapper but are here for compatibility.
    def switch_left(self):
        pass

    def switch_right(self):
        pass

    def toggle_black_white(self):
        pass