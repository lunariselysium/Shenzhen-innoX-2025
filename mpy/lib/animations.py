from neopixel import NeoPixel
from time import ticks_diff, ticks_ms

from light_manager import Animation, lerp_color


class WipeAnimation(Animation):
    def __init__(self, start_index: int, length: int, duration_ms: int, color: tuple, reverse=False):
        super().__init__(start_index, length, duration_ms)
        self.color = color
        self.reverse = reverse

    def update(self, np: NeoPixel) -> bool:
        elapsed = ticks_diff(ticks_ms(), self.start_time)
        step = int((elapsed / self.duration_ms) * self.length)

        if step >= self.length:
            for i in range(self.length):
                np[self.start_index + i] = self.color
            return False  # Done

        for i in range(self.length):
            idx = self.length - 1 - i if self.reverse else i
            np[self.start_index + idx] = self.color if i <= step else (0, 0, 0)
        return True


class SingleBlockWipeAnimation(Animation):
    """
    Sends a single block flying across the segment, starting before
    the segment (off-screen) and ending off-screen beyond the segment.
    """

    def __init__(self, start_index: int, segment_length: int, block_length: int, duration_ms: int, color: tuple,
                 reverse=False):
        # The "length" in Animation is the visible segment length
        super().__init__(start_index, segment_length, duration_ms)
        self.block_length = block_length
        self.color = color
        self.reverse = reverse

        # Total travel distance = segment length + block length (start off-screen to end off-screen)
        self.travel_length = self.length + self.block_length

    def update(self, np) -> bool:
        elapsed = ticks_diff(ticks_ms(), self.start_time)
        progress = elapsed / self.duration_ms

        if progress >= 1.0:
            # Clear the segment LEDs at the end (block fully off-screen)
            for i in range(self.length):
                idx = self.start_index + i if self.reverse else self.start_index + (self.length - 1 - i)
                np[idx] = (0, 0, 0)
            return False  # Animation finished

        # Always calculate progress left-to-right, block starting at -block_length
        block_start_pos = int(progress * self.travel_length) - self.block_length

        # Clear all LEDs in segment first
        for i in range(self.length):
            idx = self.start_index + i if self.reverse else self.start_index + (self.length - 1 - i)
            np[idx] = (0, 0, 0)

        # Draw block only inside visible segment bounds
        for i in range(self.block_length):
            led_pos = block_start_pos + i
            if 0 <= led_pos < self.length:
                idx = self.start_index + led_pos if self.reverse else self.start_index + (self.length - 1 - led_pos)
                np[idx] = self.color

        return True  # Animation ongoing


class ColorTransitionAnimation(Animation):
    """
    Fades segment to target color over time, or instantly if specified
    """

    def __init__(self, start_index: int, segment_length: int, duration_ms: int, target_color: tuple):
        super().__init__(start_index, segment_length, duration_ms)
        self.target_color = target_color
        self.start_colors = [(0, 0, 0)] * segment_length  # We'll sample on first update
        self.initialized = False

    def update(self, np):
        if not self.initialized:
            # Sample current colors of the segment
            self.start_colors = [np[self.start_index + i] for i in range(self.length)]
            self.initialized = True

            if self.duration_ms == 0:
                # Immediate fill - set target color and finish right away
                for i in range(self.length):
                    np[self.start_index + i] = self.target_color
                return False  # Animation done immediately

        elapsed = ticks_diff(ticks_ms(), self.start_time)
        t = min(elapsed / self.duration_ms, 1.0)

        for i in range(self.length):
            c = lerp_color(self.start_colors[i], self.target_color, t)
            np[self.start_index + i] = c

        if t >= 1.0:
            return False  # Finished fading
        return True
