
# src/drums.py

from .note import Note  # Assuming you have a Note class; adjust if needed
from .track import Track  # Or whatever your track class is
from .clock import Clock  # If you have BPM/clock handling
import random
import time

# General MIDI Drum Note Numbers (Channel 9 = MIDI 10)
DRUMS = {
    "kick": 36,          # Bass Drum 1 (most common kick)
    "kick_acoustic": 35, # Acoustic Bass Drum
    "snare": 38,         # Acoustic Snare
    "snare_electric": 40,
    "clap": 39,          # Hand Clap
    "rim": 37,           # Side Stick / Rimshot
    "closed_hihat": 42,
    "open_hihat": 46,
    "pedal_hihat": 44,
    "crash": 49,
    "crash2": 57,
    "ride": 51,
    "ride_bell": 53,
    "low_tom": 41,
    "mid_tom": 45,
    "high_tom": 50,
    "cowbell": 56,
    "tambourine": 54,
}

class DrumPattern:
    """
    High-level drum pattern builder.
    Usage:
        beat = DrumPattern(bpm=120)
        beat.kick.on(1, 3) \
            .snare.on(2, 4) \
            .closed_hihat.sixteenth()
        beat.play(loop=4)
    """
    def __init__(self, bpm: int = 120, steps: int = 16, channel: int = 9):
        self.bpm = bpm
        self.steps = steps          # Resolution: 16 = sixteenth notes (common for drums)
        self.channel = channel
        self.events = []            # List of (step, note_number, velocity)
        self.velocity = 100         # Default velocity
        self.humanize_time = 0.0    # Max random offset in seconds
        self.humanize_vel = 0       # Max random velocity variation

    # Helpers for common elements
    @property
    def kick(self):
        self._current_note = DRUMS["kick"]
        return self

    @property
    def snare(self):
        self._current_note = DRUMS["snare"]
        return self

    @property
    def clap(self):
        self._current_note = DRUMS["clap"]
        return self

    @property
    def closed_hihat(self):
        self._current_note = DRUMS["closed_hihat"]
        return self

    @property
    def open_hihat(self):
        self._current_note = DRUMS["open_hihat"]
        return self

    @property
    def ride(self):
        self._current_note = DRUMS["ride"]
        return self

    # Place hits on specific beats (1-based, within a 4/4 bar)
    def on(self, *beats: int, velocity: int = None):
        vel = velocity or self.velocity
        step_size = self.steps // 4  # Steps per quarter note
        for beat in beats:
            if 1 <= beat <= 4:
                step = (beat - 1) * step_size
                self.events.append((step, self._current_note, vel))
        return self

    # Repeating rhythms
    def eighth(self, velocity: int = None):
        return self._repeat_every(2, velocity)

    def sixteenth(self, velocity: int = None):
        return self._repeat_every(1, velocity)

    def _repeat_every(self, interval_steps: int, velocity: int = None):
        vel = velocity or self.velocity
        for step in range(0, self.steps, interval_steps):
            self.events.append((step, self._current_note, vel))
        return self

    # Human feel
    def humanize(self, time: float = 0.02, velocity: int = 15):
        self.humanize_time = time
        self.humanize_vel = velocity
        return self

    # Playback
    def play(self, loop: int = 1, duration: float = 0.1):  # Short note duration for drums
        step_duration = (60 / self.bpm) / (self.steps // 4)  # Seconds per step

        for _ in range(loop):
            for step, note_num, vel in sorted(self.events):
                # Wait until this step
                time.sleep(step * step_duration - Clock.current_time if hasattr(Clock, 'current_time') else 0)

                adjusted_vel = vel
                adjusted_time = 0
                if self.humanize_vel:
                    adjusted_vel = max(1, vel + random.randint(-self.humanize_vel, self.humanize_vel))
                if self.humanize_time:
                    adjusted_time = random.uniform(-self.humanize_time, self.humanize_time)

                # Send note_on + quick note_off
                Note(note_num, velocity=adjusted_vel, channel=self.channel).play(duration=duration + adjusted_time)

            # Reset for next loop if needed
            time.sleep((self.steps * step_duration) - (len(self.events) * duration if self.events else 0))

    # Presets
    @classmethod
    def basic_rock(cls, bpm=120):
        beat = cls(bpm=bpm)
        beat.kick.on(1, 3).snare.on(2, 4).closed_hihat.eighth()
        return beat

    @classmethod
    def four_on_floor(cls, bpm=128):  # House / Techno
        beat = cls(bpm=bpm)
        beat.kick.on(1, 2, 3, 4).closed_hihat.sixteenth().open_hihat.on(4)
        return beat

    @classmethod
    def trap(cls, bpm=140):
        beat = cls(bpm=bpm)
        beat.kick.on(1, 4).snare.on(3).closed_hihat.sixteenth(velocity=80)
        return beat

    @classmethod
    def boom_bap(cls, bpm=90):  # Classic hip-hop
        beat = cls(bpm=bpm)
        beat.kick.on(1, 2.5, 4).snare.on(2, 4).closed_hihat.eighth(velocity=70)
        return beat