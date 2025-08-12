import bluetooth
from micropython import const
from time import sleep

# IRQ constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

# MIDI BLE UUIDs
_MIDI_SERVICE_UUID = bluetooth.UUID("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
_MIDI_IO_CHAR_UUID = bluetooth.UUID("7772E5DB-3868-4112-A1A9-F2669D106BF3")

# MIDI service definition
MIDI_SERVICE = (
    _MIDI_SERVICE_UUID,
    (
        (
            _MIDI_IO_CHAR_UUID,
            bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY,
        ),
    ),
)


# Note definitions
def _generate_key_midi_mapping():
    note_mapping = {}
    midi = 21  # Start from A0
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_index = 0

    while midi <= 108:  # Up to C8
        note_base = notes[note_index]
        octave = (midi // 12) - 1
        note_name = f"{note_base}{octave}"
        note_mapping[note_name] = midi

        note_index = (note_index + 1) % len(notes)
        midi += 1

    return note_mapping

NOTE = _generate_key_midi_mapping()


def advertising_payload(limited_discoverable=False, br_edr=False, name=None, services=None, appearance=0):
    """
    Generate BLE advertising payload.

    Args:
        limited_discoverable (bool): Enable limited discoverable mode.
        br_edr (bool): Enable BR/EDR support.
        name (str): Device name for scan response.
        services (list): List of service UUIDs to advertise.
        appearance (int): Device appearance value.

    Returns:
        bytearray: Advertising payload.
    """
    payload = bytearray()

    def _append(ad_type, value_bytes):
        payload.extend(bytes((len(value_bytes) + 1, ad_type)))
        payload.extend(value_bytes)

    # Flags
    flags = bytearray((0x02 if limited_discoverable else 0x01) | 0x04, )
    _append(0x01, flags)

    # Service UUIDs
    if services:
        for uuid in services:
            b = bytes(uuid)
            _append(0x07, b)

    # Name (for scan response)
    if name:
        _append(0x09, name.encode())

    return payload


class BLEMidi:
    """
    BLE MIDI instrument class for sending MIDI messages over Bluetooth.

    Args:
        ble (bluetooth.BLE): Bluetooth Low Energy object.
        name (str): Name of the device for advertising (default: "Pico-W-MIDI").
    """

    def __init__(self, ble, name="Pico-W-MIDI"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((MIDI_SERVICE,))
        self._connections = set()

        # Start advertising
        adv_data = advertising_payload(services=[_MIDI_SERVICE_UUID])
        scan_data = advertising_payload(name=name)
        self._ble.gap_advertise(500000, adv_data=adv_data, resp_data=scan_data)

    def _irq(self, event, data):
        """
        Handle BLE interrupts.

        Args:
            event (int): Event type (e.g., connect, disconnect).
            data (tuple): Event data.
        """
        if event == _IRQ_CENTRAL_CONNECT:
            conn, _, _ = data
            self._connections.add(conn)
            print("Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn, _, _ = data
            self._connections.remove(conn)
            # Re-advertise on disconnect
            adv_data = advertising_payload(services=[_MIDI_SERVICE_UUID])
            scan_data = advertising_payload(name="Pico-W-MIDI")
            self._ble.gap_advertise(30000, adv_data=adv_data, resp_data=scan_data)
            print("Disconnected")

    def send(self, midi_msg):
        """
        Send a MIDI message to all connected devices.

        Args:
            midi_msg (bytearray): MIDI message to send.
        """
        header = 0x80
        timestamp = 0x80
        pkt = bytearray((header, timestamp)) + midi_msg
        for conn in self._connections:
            self._ble.gatts_notify(conn, self._handle, pkt)

    def note_on(self, note_number, velocity=127):
        """
        Send a MIDI Note On message.

        Args:
            note_number (int): MIDI note number (0-127).
            velocity (int): Note velocity (0-127, default: 127).
        """
        note_on = bytearray([0x90, note_number, velocity])
        self.send(note_on)

    def note_off(self, note_number, velocity=0):
        """
        Send a MIDI Note Off message.

        Args:
            note_number (int): MIDI note number (0-127).
            velocity (int): Note velocity (0-127, default: 0).
        """
        note_off_message = bytearray([0x80, note_number, velocity])
        self.send(note_off_message)

    def send_note(self, note_number, velocity=127, duration_s=1):
        """
        Send a MIDI Note on message, then send an off message after set interval

        Args:
            note_number (int): MIDI note number (0-127).
            velocity (int): Note velocity (0-127, default: 0).
        """
        note_on = bytearray([0x90, note_number, velocity])
        self.send(note_on)
        sleep(duration_s)
        note_off_message = bytearray([0x80, note_number, velocity])
        self.send(note_off_message)

    def control_change(self, controller, value, channel=0):
        """
        Send a MIDI Control Change (CC) message.

        Args:
            controller (int): Controller number (0-127, e.g., 7 for volume).
            value (int): Controller value (0-127).
            channel (int): MIDI channel (0-15, default: 0 which corresponds to MIDI channel 1).
        """
        # Control Change status byte: 0xB0 + channel
        status = 0xB0 + channel
        cc_msg = bytearray([status, controller, value])
        self.send(cc_msg)

    def set_volume(self, value, channel=0):
        """
        Set the volume using MIDI CC 7 (Channel Volume MSB).

        Args:
            value (int): Volume value (0-127).
            channel (int): MIDI channel (0-15, default: 0).
        """
        self.control_change(7, value, channel=channel)