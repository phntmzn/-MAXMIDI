"""
MIDI message construction helpers.

All functions return a 3-tuple:
    (status, data1, data2)

These tuples are intended to be passed directly
to MidiOut.send(status, data1, data2).
"""

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def _clamp7(value):
    """Clamp to 7-bit unsigned int (0–127)."""
    return max(0, min(127, int(value)))


def _clamp_channel(channel):
    """Clamp MIDI channel to 0–15."""
    return max(0, min(15, int(channel)))


# -------------------------------------------------
# Channel Voice Messages
# -------------------------------------------------

def note_on(note, velocity=100, channel=0):
    return (
        0x90 | _clamp_channel(channel),
        _clamp7(note),
        _clamp7(velocity),
    )


def note_off(note, velocity=0, channel=0):
    return (
        0x80 | _clamp_channel(channel),
        _clamp7(note),
        _clamp7(velocity),
    )


def poly_aftertouch(note, pressure, channel=0):
    return (
        0xA0 | _clamp_channel(channel),
        _clamp7(note),
        _clamp7(pressure),
    )


def control_change(controller, value, channel=0):
    return (
        0xB0 | _clamp_channel(channel),
        _clamp7(controller),
        _clamp7(value),
    )


def program_change(program, channel=0):
    # Program Change is 2 bytes, but we pad to 3 for uniformity
    return (
        0xC0 | _clamp_channel(channel),
        _clamp7(program),
        0,
    )


def channel_aftertouch(pressure, channel=0):
    return (
        0xD0 | _clamp_channel(channel),
        _clamp7(pressure),
        0,
    )


def pitch_bend(value, channel=0):
    """
    value: -8192 .. 8191
    """
    value = int(value)
    value = max(-8192, min(8191, value)) + 8192

    lsb = value & 0x7F
    msb = (value >> 7) & 0x7F

    return (
        0xE0 | _clamp_channel(channel),
        lsb,
        msb,
    )


# -------------------------------------------------
# System Common Messages
# -------------------------------------------------

def song_position_pointer(position):
    """
    position: number of MIDI beats (16th notes)
    """
    position = max(0, min(0x3FFF, int(position)))
    return (
        0xF2,
        position & 0x7F,
        (position >> 7) & 0x7F,
    )


def song_select(song):
    return (
        0xF3,
        _clamp7(song),
        0,
    )


def tune_request():
    return (0xF6, 0, 0)


# -------------------------------------------------
# System Real-Time Messages
# (data bytes ignored, but padded for consistency)
# -------------------------------------------------

def clock():
    return (0xF8, 0, 0)


def start():
    return (0xFA, 0, 0)


def continue_():
    return (0xFB, 0, 0)


def stop():
    return (0xFC, 0, 0)


def active_sensing():
    return (0xFE, 0, 0)


def reset():
    return (0xFF, 0, 0)


# -------------------------------------------------
# SysEx (variable length)
# -------------------------------------------------

def sysex(data):
    """
    data: iterable of ints (0–127)
    Returns a bytes object instead of a 3-tuple.
    """
    payload = bytes(_clamp7(b) for b in data)
    return bytes([0xF0]) + payload + bytes([0xF7])