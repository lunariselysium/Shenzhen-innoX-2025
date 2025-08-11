from machine import Pin
from lib.light_manager import LightManager
from lib.animations import *
import time

lm = LightManager(Pin(1, Pin.OUT), total_count = 100, segment_count = 5)

segment_starts = [
    lm.get_segment_start(0),
    lm.get_segment_start(1),
    lm.get_segment_start(2),
    lm.get_segment_start(3),
    lm.get_segment_start(4),
]

segment_length = lm.segment_length

animations = [
    SingleBlockWipeAnimation(segment_starts[0], segment_length, 10, 1000, (255, 0, 0)),
    SingleBlockWipeAnimation(segment_starts[1], segment_length,  10, 1000, (0, 255, 0)),
]

delays = [
    1000,
    2000,
]

lm.add_sequence(animations, delays, replay_count=5)

while True:
    lm.update()
    time.sleep(0.1)