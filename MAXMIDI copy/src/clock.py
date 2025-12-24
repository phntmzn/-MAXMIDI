"""
MIDI Clock and Transport control.

- Internal clock generation
- BPM / PPQN control
- MIDI Start / Stop / Continue
"""

import time
import threading

from .message import clock as clock_msg
from .message import start as start_msg
from .message import stop as stop_msg
from .message import continue_ as continue_msg


DEFAULT_PPQN = 24  # MIDI clock pulses per quarter note


class MidiClock:
    """
    MIDI clock generator.

    Example:
        from maxmidi import Midi, MidiClock

        midi = Midi()
        midi.open()

        clock = MidiClock(midi, bpm=120)
        clock.start()
        time.sleep(5)
        clock.stop()
    """

    def __init__(self, midi, bpm=120.0, ppqn=DEFAULT_PPQN):
        self.midi = midi
        self.bpm = float(bpm)
        self.ppqn = int(ppqn)

        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    # -------------------------------------------------
    # Properties
    # -------------------------------------------------

    @property
    def interval(self):
        """
        Seconds between MIDI clock ticks.
        """
        return 60.0 / (self.bpm * self.ppqn)

    # -------------------------------------------------
    # Transport
    # -------------------------------------------------

    def start(self):
        """
        Send MIDI Start and begin clock ticks.
        """
        with self._lock:
            if self._running:
                return

            self._running = True

            # Send MIDI Start
            self._send(start_msg())

            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
            )
            self._thread.start()

    def stop(self):
        """
        Stop clock ticks and send MIDI Stop.
        """
        with self._lock:
            if not self._running:
                return

            self._running = False

        # Send MIDI Stop
        self._send(stop_msg())

    def continue_(self):
        """
        Send MIDI Continue and resume clock ticks.
        """
        with self._lock:
            if self._running:
                return

            self._running = True

            self._send(continue_msg())

            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
            )
            self._thread.start()

    # -------------------------------------------------
    # Clock loop
    # -------------------------------------------------

    def _run(self):
        next_tick = time.perf_counter()

        while True:
            with self._lock:
                if not self._running:
                    break
                interval = self.interval

            next_tick += interval
            self._send(clock_msg())

            sleep_time = next_tick - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _send(self, msg):
        """
        Send a MIDI message tuple.
        """
        if hasattr(self.midi, "send"):
            self.midi.send(*msg)
        else:
            # Assume MidiOut-like object
            self.midi.send(*msg)

    # -------------------------------------------------
    # Configuration
    # -------------------------------------------------

    def set_bpm(self, bpm):
        with self._lock:
            self.bpm = float(bpm)

    def set_ppqn(self, ppqn):
        with self._lock:
            self.ppqn = int(ppqn)