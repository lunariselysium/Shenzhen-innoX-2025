from machine import Pin
from lib.light_manager import LightManager
from lib.animations import *
import time
from lib.animations import SingleBlockWipeAnimation

data = [[3], [3], [3], [3], [4], [4], [5], [5], [5], [5], [4], [4], [3], [3], [2], [2], [1], [1], [1], [1], [2], [2], [3], [3], [3], [3], [3], [2], [2], [0], [0], [0], [3], [3], [3], [3], [4], [4], [5], [5], [5], [5], [4], [4], [4], [3], [3], [2], [2], [1], [1], [1], [1], [2], [2], [3], [3], [2], [2], [2], [1], [1], [0], [0], [0], [2], [2], [2], [2], [3], [3], [1], [1], [2], [2], [3], [4], [3], [3], [1], [1],[2,4],[3,5],[4],[3,5],[3,5],[2,4],[2,4],[1,3],[1,3],[2,4],[2,4],[5],[5],[3],[3],[3],[3],[3],[3],[4],[4],[5],[5],[5], [5], [4], [4], [3], [3], [2], [2], [1], [1], [1], [1], [2], [2], [3], [3], [3], [3],[2],[2],[2],[1],[1],[1],[1,2],[3,4,5]]

loc =  [ 1, 2, 3, 4,5,6,7]

SIXTEENTH_NOTE_LENGTH = 30 # ms
a = SIXTEENTH_NOTE_LENGTH

R = (255,0,0)
G = (0,255,0)
B = (0,0,255)

lm = LightManager(Pin(9, Pin.OUT), total_count = 25, segment_count = 5)
segment_length = lm.segment_length
segment_starts = [
    lm.get_segment_start(4),
    lm.get_segment_start(3),
    lm.get_segment_start(2),
    lm.get_segment_start(1),
    lm.get_segment_start(0),
]

animations_and_delays = {}
lm_index = 0
for i in data:
    for j in i:
        if j != 0:
            scra2 = loc.index(int(j))
            animations_and_delays.setdefault(SingleBlockWipeAnimation(segment_starts[scra2], segment_length, 5, a*16, R), a*16*lm_index)
    lm_index += 1
segment_length = lm.segment_length
'''
animations_and_delays = {
SingleBlockWipeAnimation(segment_starts[2], segment_length, 10, a*16, R): 0,
SingleBlockWipeAnimation(segment_starts[2], segment_length, 10, a*16, G): a*16,
SingleBlockWipeAnimation(segment_starts[3], segment_length, 10, a*16, B): a*16*2,
SingleBlockWipeAnimation(segment_starts[4], segment_length, 10, a*16, R): a*16*3,
}
'''
lm.add_sequence(list(animations_and_delays.keys()), list(animations_and_delays.values()), replay_count=5)

while True:
    lm.update()
    time.sleep(0.02)