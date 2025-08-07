import bluetooth
import time
from ble_midi_instrument import BLEMidi, NOTE

# Initialize BLE
ble = bluetooth.BLE()
midi = BLEMidi(ble, name="PicoMIDI")

# Play a C major chord repeatedly when connected
while True:
    if midi._connections:  # Check if there are active connections
        print("→ Note On")
        midi.note_on(NOTE['C4'])  # Play C4
        midi.note_on(NOTE['E4'])  # Play E4
        midi.note_on(NOTE['G4'])  # Play G4
        time.sleep(1)
        print("→ Note Off")
        midi.note_off(NOTE['C4'])  # Stop C4
        midi.note_off(NOTE['E4'])  # Stop E4
        midi.note_off(NOTE['G4'])  # Stop G4
        time.sleep(1)