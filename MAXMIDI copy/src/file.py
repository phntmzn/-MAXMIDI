"""
Standard MIDI File (SMF) read/write support.

Supports:
- Type 0 and Type 1 MIDI files
- Tempo, time signature, key signature
- Note on / note off events
"""

import struct
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# -------------------------------------------------
# Utilities
# -------------------------------------------------

def _varlen(value: int) -> bytes:
    """Encode variable-length quantity."""
    buffer = value & 0x7F
    out = []

    while True:
        out.append(buffer & 0xFF)
        if value <= 0x7F:
            break
        value >>= 7
        buffer = (value & 0x7F) | 0x80

    return bytes(reversed(out))


def _read_varlen(data: bytes, idx: int) -> Tuple[int, int]:
    """Decode variable-length quantity."""
    value = 0
    while True:
        byte = data[idx]
        idx += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, idx


# -------------------------------------------------
# Events
# -------------------------------------------------

@dataclass
class MidiEvent:
    delta: int
    status: int
    data: bytes = b""


@dataclass
class MetaEvent:
    delta: int
    meta_type: int
    data: bytes = b""


# -------------------------------------------------
# Track
# -------------------------------------------------

@dataclass
class MidiTrack:
    events: List[object] = field(default_factory=list)

    def add_event(self, event):
        self.events.append(event)

    def note_on(self, delta, note, velocity, channel=0):
        self.add_event(
            MidiEvent(delta, 0x90 | channel, bytes([note, velocity]))
        )

    def note_off(self, delta, note, velocity=0, channel=0):
        self.add_event(
            MidiEvent(delta, 0x80 | channel, bytes([note, velocity]))
        )

    def tempo(self, delta, bpm):
        mpqn = int(60_000_000 / bpm)
        self.add_event(
            MetaEvent(delta, 0x51, struct.pack(">I", mpqn)[1:])
        )

    def time_signature(self, delta, num, denom):
        self.add_event(
            MetaEvent(delta, 0x58, bytes([num, denom.bit_length() - 1, 24, 8]))
        )

    def key_signature(self, delta, key, minor=0):
        self.add_event(
            MetaEvent(delta, 0x59, struct.pack("bb", key, minor))
        )


# -------------------------------------------------
# MIDI File
# -------------------------------------------------

@dataclass
class MidiFile:
    type: int = 1
    ticks_per_quarter: int = 480
    tracks: List[MidiTrack] = field(default_factory=list)

    def add_track(self) -> MidiTrack:
        track = MidiTrack()
        self.tracks.append(track)
        return track

    # -------------------------------------------------
    # Write
    # -------------------------------------------------

    def save(self, path: str):
        with open(path, "wb") as f:
            # Header chunk
            f.write(b"MThd")
            f.write(struct.pack(">IHHH", 6, self.type, len(self.tracks), self.ticks_per_quarter))

            # Track chunks
            for track in self.tracks:
                track_data = bytearray()

                for event in track.events:
                    track_data += _varlen(event.delta)

                    if isinstance(event, MidiEvent):
                        track_data.append(event.status)
                        track_data += event.data

                    elif isinstance(event, MetaEvent):
                        track_data += bytes([0xFF, event.meta_type])
                        track_data += _varlen(len(event.data))
                        track_data += event.data

                # End of Track
                track_data += _varlen(0)
                track_data += b"\xFF\x2F\x00"

                f.write(b"MTrk")
                f.write(struct.pack(">I", len(track_data)))
                f.write(track_data)

    # -------------------------------------------------
    # Read (basic)
    # -------------------------------------------------

    @classmethod
    def load(cls, path: str) -> "MidiFile":
        with open(path, "rb") as f:
            data = f.read()

        idx = 0

        if data[idx:idx+4] != b"MThd":
            raise ValueError("Invalid MIDI file")

        idx += 4
        _, mtype, ntracks, division = struct.unpack(">IHHH", data[idx:idx+10])
        idx += 10

        midi = cls(type=mtype, ticks_per_quarter=division)

        for _ in range(ntracks):
            if data[idx:idx+4] != b"MTrk":
                raise ValueError("Invalid track chunk")
            idx += 4

            length = struct.unpack(">I", data[idx:idx+4])[0]
            idx += 4
            track_end = idx + length

            track = MidiTrack()
            midi.tracks.append(track)

            running_status = None

            while idx < track_end:
                delta, idx = _read_varlen(data, idx)
                status = data[idx]

                if status < 0x80:
                    status = running_status
                else:
                    idx += 1
                    running_status = status

                if status == 0xFF:
                    meta_type = data[idx]
                    idx += 1
                    size, idx = _read_varlen(data, idx)
                    meta_data = data[idx:idx+size]
                    idx += size
                    track.add_event(MetaEvent(delta, meta_type, meta_data))
                else:
                    size = 1 if status & 0xF0 in (0xC0, 0xD0) else 2
                    ev_data = data[idx:idx+size]
                    idx += size
                    track.add_event(MidiEvent(delta, status, ev_data))

        return midi