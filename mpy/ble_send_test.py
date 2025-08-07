import bluetooth
import random
import struct
import time
from micropython import const

# Constants for Bluetooth IRQ events
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

# Flags for characteristic properties
_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)

# Define the UUIDs for our custom service and characteristic
_SERVICE_UUID = bluetooth.UUID("b9e3a680-457c-11ed-b878-0242ac120002")
_CHAR_UUID = bluetooth.UUID("c9e3a680-457c-11ed-b878-0242ac120002")

# Define the advertising payload
_ADV_PAYLOAD = bytearray()
_ADV_PAYLOAD += struct.pack('B', 2)  # Length of this section
_ADV_PAYLOAD += struct.pack('B', 0x01) # Flags
_ADV_PAYLOAD += struct.pack('B', 0x06) # General Discoverable Mode, BR/EDR Not Supported
_ADV_PAYLOAD += struct.pack('B', len("PicoNotes") + 1) # Length of this section
_ADV_PAYLOAD += struct.pack('B', 0x09) # Complete Local Name
_ADV_PAYLOAD += "PicoNotes".encode()

# Define the musical service
_MUSICAL_SERVICE = (
    _SERVICE_UUID,
    (
        (_CHAR_UUID, _FLAG_READ | _FLAG_NOTIFY),
    ),
)

class BLEMusicalPeripheral:
    def __init__(self, ble, name="PicoNotes"):
        self._ble = ble
        self._ble.active(True)
        self._ble.config(gap_name=name)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_MUSICAL_SERVICE,))
        self._connections = set()
        self._advertise()

    def _irq(self, event, data):
        """Interrupt request handler."""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            self._advertise()

    def send_note(self, note):
        """Encodes and sends a note to connected devices."""
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle, note.encode())

    def _advertise(self, interval_us=30000):
        """Starts advertising the device."""
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=_ADV_PAYLOAD)

if __name__ == "__main__":
    ble = bluetooth.BLE()
    p = BLEMusicalPeripheral(ble)
    print(':'.join(f'{b:02X}' for b in ble.config('mac')[1]))
    
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']

    while True:
        if p._connections:
            # Choose 1 to 3 random notes to play simultaneously
            num_notes = random.randint(1, 3)
            notes_to_play = ['C4','E4']
            
            # Send "note on" for each selected note
            for note in notes_to_play:
                p.send_note(f"{note}:1")
                print(f"Sending note on: {note}")
            
            time.sleep(1)  # Play notes for 1 second
            
            # Send "note off" for each selected note
            for note in notes_to_play:
                p.send_note(f"{note}:0")
                print(f"Sending note off: {note}")
            
            time.sleep(1)  # Wait 1 second before next cycle
        else:
            time.sleep(1)