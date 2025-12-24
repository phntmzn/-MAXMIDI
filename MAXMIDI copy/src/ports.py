"""
MIDI port discovery and helpers.

This module provides a simple, stable API for:
- listing MIDI input/output ports
- opening ports by index or name
"""

from .in import MidiIn
from .out import MidiOut


# -------------------------------------------------
# Port listing
# -------------------------------------------------

def list_inputs():
    """
    Return a list of available MIDI input port names.
    """
    ports = []
    midi = MidiIn()

    try:
        count = midi.get_port_count()
        for i in range(count):
            ports.append(midi.get_port_name(i))
    finally:
        midi.close()

    return ports


def list_outputs():
    """
    Return a list of available MIDI output port names.
    """
    ports = []
    midi = MidiOut()

    try:
        count = midi.get_port_count()
        for i in range(count):
            ports.append(midi.get_port_name(i))
    finally:
        midi.close()

    return ports


# -------------------------------------------------
# Port open helpers
# -------------------------------------------------

def open_input(port):
    """
    Open an input port by index or name.
    """
    midi = MidiIn()

    if isinstance(port, int):
        midi.open(port)
        return midi

    ports = list_inputs()
    if port not in ports:
        raise ValueError(f"MIDI input port not found: {port}")

    midi.open(ports.index(port))
    return midi


def open_output(port):
    """
    Open an output port by index or name.
    """
    midi = MidiOut()

    if isinstance(port, int):
        midi.open(port)
        return midi

    ports = list_outputs()
    if port not in ports:
        raise ValueError(f"MIDI output port not found: {port}")

    midi.open(ports.index(port))
    return midi