from neopixel import NeoPixel
from machine import Pin
import time



def lerp_color(c1, c2, t):
    """Linear interpolate between two colors c1 and c2 by t (0..1)."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


class Animation:
    """Base class for LED animations."""
    def __init__(self, start_index: int, length: int, duration_ms: int):
        self.start_index = start_index
        self.length = length
        self.duration_ms = duration_ms
        self.start_time = time.ticks_ms()

    def update(self, np: NeoPixel) -> bool:
        """Update LEDs for this frame. Return False if finished."""
        raise NotImplementedError

    def reset(self) -> None:
        """Reset Animation start time."""
        self.start_time = time.ticks_ms()

class ScheduledAnimation:
    """Wraps an animation with a start delay."""
    def __init__(self, animation: Animation, delay_ms: int):
        self.animation = animation
        self.delay_ms = delay_ms
        self.start_time = time.ticks_ms()
        self.started = False

    def update(self, np: NeoPixel) -> bool:
        """Update the animation if its delay has passed."""
        elapsed = time.ticks_diff(time.ticks_ms(), self.start_time)
        if elapsed < self.delay_ms:
            return True  # Keep waiting

        if not self.started:
            self.animation.reset()
            self.started = True # Reset time when delay ends

        return self.animation.update(np)  # Run the animation

    def reset(self) -> None:
        """Reset Scheduled animation."""
        self.start_time = time.ticks_ms()
        self.started = False

class Sequence:
    """Represents a sequence of animations with delays and replay settings."""
    def __init__(self, animations: list, delays_ms: list, replay_count: int = 1):
        """
        Initialize a sequence.
        - animations: List of Animation objects.
        - delays_ms: List of start delays (in milliseconds) for each animation.
        - replay_count: Number of times to replay the sequence (0 for infinite).
        """
        if len(animations) != len(delays_ms):
            raise ValueError("Number of animations must match number of delays")
        self.animations = animations
        self.delays_ms = delays_ms
        self.replay_count = replay_count  # 0 for infinite, >0 for finite replays
        self.current_replay = 0
        self.scheduled_animations = []
        self.start_time = None
        self.reset()

    def reset(self):
        """Reset the sequence to start from the beginning."""
         # Reset each animation's internal state
        for anim in self.animations:
            anim.reset()
        # Recreate scheduled animations to reset delay timers
        self.scheduled_animations = [
            ScheduledAnimation(anim, delay) for anim, delay in zip(self.animations, self.delays_ms)
        ]
        self.start_time = time.ticks_ms()
        self.current_replay += 1

    def update(self, np: NeoPixel) -> bool:
        """Update all animations in the sequence. Return False if sequence is finished."""
        still_running = []
        for sched_anim in self.scheduled_animations:
            if sched_anim.update(np):
                still_running.append(sched_anim)

        self.scheduled_animations = still_running

        if not still_running:
            # Sequence iteration finished
            if self.replay_count == 0 or self.current_replay < self.replay_count:
                self.reset()
                return True
            return False  # Sequence fully done
        return True

class LightManager:
    """Controls multiple animations across LED segments."""
    def __init__(self, pin: Pin, total_count: int, segment_count: int) -> None:
        if not isinstance(pin, Pin):
            raise TypeError("pin must be a machine.Pin instance")

        self.np = NeoPixel(pin, total_count)
        self.total_count = total_count
        self.segment_count = segment_count
        self.segment_length = total_count // segment_count
        self.animations = []

    def get_segment_start(self, segment_index: int) -> int:
        """Return the starting LED index of a segment."""
        return segment_index * self.segment_length

    def add_animation(self, animation: Animation):
        self.animations.append(animation)

    def add_sequence(self, animations: list, delays_ms: list, replay_count: int = 1):
        """Add a sequence of animations with delays and replay count."""
        sequence = Sequence(animations, delays_ms, replay_count)
        self.animations.append(sequence)

    def update(self):
        """Call this in your main loop to refresh LEDs."""
        still_running = []
        for anim in self.animations:
            if anim.update(self.np):
                still_running.append(anim)
        self.animations = still_running
        self.np.write()

    def clear(self):
        """Turn off all LEDs."""
        self.np.fill((0,0,0))
        self.np.write()