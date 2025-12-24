
# src/sequencer.py

from typing import Union, List, Optional
from .chord import Chord
from .arpeggiator import Arpeggiator  # Assuming you have this
from .drums import DrumPattern
from .note import Note
import time
import random

# Type for anything that can be "played"
Playable = Union[Note, Chord, Arpeggiator, DrumPattern, "Sequencer"]

class Sequencer:
    """
    A simple, chainable sequencer for building patterns and songs.

    Examples:
        seq = Sequencer(bpm=120)
        seq << Chord("Cmaj7") << Chord("Am7", duration=2) << Arpeggiator(Chord("Fmaj7"), style="up") << rest(0.5)
        seq.play(loop=4)

        # Or with drums
        seq << DrumPattern.basic_rock() << Chord("C").arpeggiate()
    """

    def __init__(self, bpm: int = 120, steps_per_bar: int = 16, bars: int = 1):
        self.bpm = bpm
        self.steps_per_bar = steps_per_bar  # Usually 16 for 16th notes
        self.bars = bars
        self.total_steps = steps_per_bar * bars
        self.events: List[tuple[int, Playable, float]] = []  # (step, item, duration_in_beats)
        self.humanize_time: float = 0.0
        self.humanize_vel: int = 0

    @property
    def beat_duration(self) -> float:
        """Duration of one quarter note in seconds"""
        return 60.0 / self.bpm

    @property
    def step_duration(self) -> float:
        """Duration of one step (e.g., 16th note) in seconds"""
        return self.beat_duration / (self.steps_per_bar // 4)

    # Chainable adding
    def __lshift__(self, item: Union[Playable, tuple]) -> "Sequencer":
        """
        Add an item at the next available step.
        Use tuple (item, duration_in_beats) for custom duration.
        """
        if isinstance(item, tuple):
            playable, duration = item
        else:
            playable = item
            duration = 1.0  # Default: one quarter note per event

        # Find next free step
        current_step = 0
        if self.events:
            last_step, _, last_dur = max(self.events, key=lambda e: e[0])
            current_step = last_step + int(last_dur * (self.steps_per_bar // 4))

        self.at(current_step, playable, duration=duration)
        return self

    def at(self, step: int, item: Playable, duration: float = 1.0) -> "Sequencer":
        """Place an item at a specific step (0-based within the sequence)"""
        if step < 0 or step >= self.total_steps:
            raise ValueError(f"Step {step} out of bounds (0–{self.total_steps-1})")
        self.events.append((step, item, duration))
        return self

    def rest(self, beats: float = 1.0) -> "Sequencer":
        """Add silence (advances the cursor without playing)"""
        return self << (None, beats)

    def humanize(self, time: float = 0.02, velocity: int = 12) -> "Sequencer":
        """Add natural feel to all events"""
        self.humanize_time = time
        self.humanize_vel = velocity
        return self

    def loop(self, times: int = 1) -> "Sequencer":
        """Convenience: play multiple times"""
        self.play(loop=times)
        return self

    def play(self, loop: int = 1):
        """Play the sequence"""
        for _ in range(loop):
            played_steps = set()

            for step, item, duration in sorted(self.events, key=lambda e: e[0]):
                if item is None:  # Rest
                    continue

                # Wait until this step
                wait_steps = step - min(played_steps or {0})
                time.sleep(wait_steps * self.step_duration)

                # Humanization
                offset = 0.0
                vel_adjust = 0
                if self.humanize_time:
                    offset = random.uniform(-self.humanize_time, self.humanize_time)
                if self.humanize_vel and hasattr(item, "velocity"):
                    # Apply to chords/arps/notes that support velocity
                    original_vel = getattr(item, "velocity", 100)
                    vel_adjust = random.randint(-self.humanize_vel, self.humanize_vel)
                    item.velocity(original_vel + vel_adjust)

                time.sleep(max(0, offset))  # Apply time offset

                # Play the item (with its own duration handling if needed)
                if hasattr(item, "play"):
                    # For Arpeggiator, DrumPattern, etc.
                    item.play(duration=duration * self.beat_duration)
                elif isinstance(item, (Chord, Note)):
                    item.play(duration=duration * self.beat_duration)

                played_steps.add(step)

            # End of loop rest
            time.sleep(self.total_steps * self.step_duration)

    # Presets / helpers
    @classmethod
    def progression(cls, chords: List[str], key: str = None, bpm: int = 110, arpeggiate: bool = False):
        """Quick chord progression sequencer"""
        seq = cls(bpm=bpm)
        for chord_str in chords:
            chord = Chord(chord_str)
            if arpeggiate:
                seq << Arpeggiator(chord, style="up")
            else:
                seq << chord
        return seq