from machine import Pin
from light_manager import LightManager, WipeAnimation, SingleBlockWipeAnimation, ColorTransitionAnimation
import time

lm = LightManager(Pin(1, Pin.OUT), total_count = 50, segment_count = 5)

lm.add_animation(WipeAnimation(
    lm.get_segment_start(0), lm.segment_length, 1000, (255,0,0)))
lm.add_animation(ColorTransitionAnimation(
    lm.get_segment_start(1), lm.segment_length, 1000, (0,0,255)))
lm.add_animation(SingleBlockWipeAnimation(
    lm.get_segment_start(3), lm.segment_length, 10, 2000, (0,0,255), reverse=True))
lm.add_animation(SingleBlockWipeAnimation(
    lm.get_segment_start(4), lm.segment_length, 10, 500, (0,255,0)))

t = time.ticks_ms()
while True:
    lm.update()
    time.sleep_ms(20)
    if time.ticks_diff(time.ticks_ms(), t) >= 5000:
        break


lm.add_animation(ColorTransitionAnimation(
    lm.get_segment_start(0), lm.segment_length, 0, (0,0,255)))
lm.add_animation(ColorTransitionAnimation(
    lm.get_segment_start(1), lm.segment_length, 1000, (0,255,0)))


t = time.ticks_ms()
while True:
    lm.update()
    time.sleep_ms(20)
    if time.ticks_diff(time.ticks_ms(), t) >= 5000:
        break