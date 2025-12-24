"""
Chord utilities and playback helpers.
"""

from typing import List

# -------------------------------------------------
# Note name utilities
# -------------------------------------------------

NOTE_NAMES = {
    "C": 0,  "C#": 1,  "Db": 1,
    "D": 2,  "D#": 3,  "Eb": 3,
    "E": 4,
    "F": 5,  "F#": 6,  "Gb": 6,
    "G": 7,  "G#": 8,  "Ab": 8,
    "A": 9,  "A#": 10, "Bb": 10,
    "B": 11,
}


# -------------------------------------------------
# Chord formulas (intervals in semitones)
# -------------------------------------------------

CHORD_TYPES = {
    "":      [0, 4, 7],        # major
    "m":     [0, 3, 7],        # minor
    "dim":   [0, 3, 6],
    "aug":   [0, 4, 8],
    "7":     [0, 4, 7, 10],
    "maj7":  [0, 4, 7, 11],
    "m7":    [0, 3, 7, 10],
    "m7b5":  [0, 3, 6, 10],
    "sus2":  [0, 2, 7],
    "sus4":  [0, 5, 7],
    "6":     [0, 4, 7, 9],
    "9":     [0, 4, 7, 10, 14],
}


# -------------------------------------------------
# Chord class
# -------------------------------------------------

class Chord:
    """
    Represents a musical chord.

    Example:
        Chord("C")
        Chord("Am7")
        Chord("F#dim")
    """

    def __init__(self, name: str, octave: int = 4):
        self.name = name
        self.octave = octave

        self.root_name, self.chord_type = self._parse(name)
        self.root = NOTE_NAMES[self.root_name]
        self.intervals = CHORD_TYPES[self.chord_type]

    # -------------------------------------------------

    def _parse(self, name: str):
        # Root note (C, C#, Db, etc.)
        if len(name) >= 2 and name[:2] in NOTE_NAMES:
            root = name[:2]
            rest = name[2:]
        else:
            root = name[:1]
            rest = name[1:]

        if root not in NOTE_NAMES:
            raise ValueError(f"Invalid chord root: {root}")

        if rest not in CHORD_TYPES:
            raise ValueError(f"Unsupported chord type: {rest}")

        return root, rest

    # -------------------------------------------------

    def notes(self, inversion: int = 0) -> List[int]:
        """
        Return MIDI note numbers for the chord.
        """
        base = (self.octave + 1) * 12 + self.root
        notes = [base + i for i in self.intervals]

        # Apply inversion
        for _ in range(inversion):
            n = notes.pop(0)
            notes.append(n + 12)

        return notes

    # -------------------------------------------------
    # Playback helpers
    # -------------------------------------------------

    def play(self, midi, velocity=100, duration=0.5, inversion=0):
        """
        Play the chord via Midi API.
        """
        notes = self.notes(inversion)

        for n in notes:
            midi.note_on(n, velocity)

        midi.sleep(duration)

        for n in notes:
            midi.note_off(n)

    def arpeggiate(self, midi, velocity=100, step=0.1, inversion=0):
        """
        Play notes sequentially.
        """
        for n in self.notes(inversion):
            midi.note_on(n, velocity)
            midi.sleep(step)
            midi.note_off(n)


# -------------------------------------------------
# Convenience function
# -------------------------------------------------

def play_chord(midi, name, **kwargs):
    Chord(name).play(midi, **kwargs)