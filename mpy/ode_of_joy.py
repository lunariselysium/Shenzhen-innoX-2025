from machine import Pin
from lib.light_manager import LightManager
from lib.animations import *
import time

SIXTEENTH_NOTE_LENGTH = 30 # ms
a = SIXTEENTH_NOTE_LENGTH

R = (255,0,0)
G = (0,255,0)
B = (0,0,255)

lm = LightManager(Pin(1, Pin.OUT), total_count = 100, segment_count = 5)

segment_starts = [
    lm.get_segment_start(0),
    lm.get_segment_start(1),
    lm.get_segment_start(2),
    lm.get_segment_start(3),
    lm.get_segment_start(4),
]

segment_length = lm.segment_length

animations_and_delays = {
SingleBlockWipeAnimation(segment_starts[2], segment_length, 10, a*16, R): 0,
SingleBlockWipeAnimation(segment_starts[2], segment_length, 10, a*16, G): a*16,
SingleBlockWipeAnimation(segment_starts[3], segment_length, 10, a*16, B): a*16*2,
SingleBlockWipeAnimation(segment_starts[4], segment_length, 10, a*16, R): a*16*3,
}

lm.add_sequence(list(animations_and_delays.keys()), list(animations_and_delays.values()), replay_count=5)

while True:
    lm.update()
    time.sleep(0.2)
