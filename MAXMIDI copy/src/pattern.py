"""
Pattern and sequencing helpers.

Includes:
- NotePattern
- DrumPattern
- Arpeggiator
"""

import time
from typing import List, Iterable


# -------------------------------------------------
# Base Pattern
# -------------------------------------------------

class Pattern:
    """
    Base pattern class.
    """

    def __init__(self, steps: Iterable, step_time: float = 0.25):
        self.steps = list(steps)
        self.step_time = float(step_time)

    def play(self, midi, velocity=100):
        raise NotImplementedError


# -------------------------------------------------
# Note Pattern
# -------------------------------------------------

class NotePattern(Pattern):
    """
    Sequence of notes.

    steps: list of MIDI notes or None (rest)
    """

    def play(self, midi, velocity=100):
        for note in self.steps:
            if note is not None:
                midi.note_on(note, velocity)
            midi.sleep(self.step_time)
            if note is not None:
                midi.note_off(note)


# -------------------------------------------------
# Drum Pattern
# -------------------------------------------------

class DrumPattern(Pattern):
    """
    Drum pattern (channel 10 / index 9).

    steps: list of MIDI drum notes or lists of notes
    """

    DRUM_CHANNEL = 9

    def play(self, midi, velocity=100):
        for step in self.steps:
            notes = step if isinstance(step, (list, tuple)) else [step]

            for note in notes:
                if note is not None:
                    midi.note_on(note, velocity, channel=self.DRUM_CHANNEL)

            midi.sleep(self.step_time)

            for note in notes:
                if note is not None:
                    midi.note_off(note, channel=self.DRUM_CHANNEL)


# -------------------------------------------------
# Arpeggiator
# -------------------------------------------------

class Arpeggiator:
    """
    Arpeggiator for chords.

    modes: up, down, updown, random
    """

    def __init__(self, notes: List[int], step_time=0.1, mode="up"):
        self.notes = list(notes)
        self.step_time = float(step_time)
        self.mode = mode

    def _order(self):
        if self.mode == "up":
            return self.notes
        if self.mode == "down":
            return list(reversed(self.notes))
        if self.mode == "updown":
            return self.notes + list(reversed(self.notes[1:-1]))
        if self.mode == "random":
            import random
            notes = self.notes[:]
            random.shuffle(notes)
            return notes
        return self.notes

    def play(self, midi, velocity=100):
        for note in self._order():
            midi.note_on(note, velocity)
            midi.sleep(self.step_time)
            midi.note_off(note)


# -------------------------------------------------
# Loop helper
# -------------------------------------------------

def loop(pattern, midi, velocity=100, times=None):
    """
    Repeat a pattern.

    times=None => infinite
    """
    count = 0
    while times is None or count < times:
        pattern.play(midi, velocity)
        count += 1