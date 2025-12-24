"""
High-level public API for MaxMIDI.

This module is what users should import.
It hides ctypes / backend details and exposes
a musical, Pythonic interface.
"""

import time
from contextlib import contextmanager

from .out import MidiOut
from .message import (
    note_on,
    note_off,
    control_change,
    program_change,
    pitch_bend,
)


class Midi:
    """
    High-level MIDI output interface.

    Example:
        from maxmidi import Midi

        with Midi() as m:
            m.note_on(60)
            m.sleep(0.5)
            m.note_off(60)
    """

    def __init__(self, port=None, channel=0):
        self.port = port
        self.channel = channel
        self._out = MidiOut()
        self._opened = False

    # -------------------------------------------------
    # Context manager
    # -------------------------------------------------

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # -------------------------------------------------
    # Port control
    # -------------------------------------------------

    def open(self):
        if not self._opened:
            if self.port is None:
                self._out.open_default()
            else:
                self._out.open(self.port)
            self._opened = True

    def close(self):
        if self._opened:
            self._out.close()
            self._opened = False

    # -------------------------------------------------
    # Timing helpers
    # -------------------------------------------------

    @staticmethod
    def sleep(seconds: float):
        time.sleep(seconds)

    # -------------------------------------------------
    # MIDI send helpers
    # -------------------------------------------------

    def send(self, status, data1=0, data2=0):
        self._out.send(status, data1, data2)

    # -------------------------------------------------
    # Musical commands
    # -------------------------------------------------

    def note_on(self, note, velocity=100, channel=None):
        ch = self.channel if channel is None else channel
        msg = note_on(note, velocity, ch)
        self._out.send(*msg)

    def note_off(self, note, velocity=0, channel=None):
        ch = self.channel if channel is None else channel
        msg = note_off(note, velocity, ch)
        self._out.send(*msg)

    def play_note(self, note, velocity=100, duration=0.5, channel=None):
        self.note_on(note, velocity, channel)
        time.sleep(duration)
        self.note_off(note, 0, channel)

    def control_change(self, controller, value, channel=None):
        ch = self.channel if channel is None else channel
        msg = control_change(controller, value, ch)
        self._out.send(*msg)

    def program_change(self, program, channel=None):
        ch = self.channel if channel is None else channel
        msg = program_change(program, ch)
        self._out.send(*msg)

    def pitch_bend(self, value, channel=None):
        """
        value: -8192 .. 8191
        """
        ch = self.channel if channel is None else channel
        msg = pitch_bend(value, ch)
        self._out.send(*msg)


# -----------------------------------------------------
# Convenience factory
# -----------------------------------------------------

def open_midi(port=None, channel=0):
    """
    Quick helper:

        m = open_midi()
        m.note_on(60)
    """
    midi = Midi(port=port, channel=channel)
    midi.open()
    return midi