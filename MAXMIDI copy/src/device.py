
"""
MIDI device abstraction.

A MidiDevice represents a single MIDI input or output port,
with metadata and convenience helpers.
"""

from dataclasses import dataclass
from typing import Optional

from .ports import list_inputs, list_outputs


@dataclass(frozen=True)
class MidiDevice:
    """
    Represents a MIDI device/port.
    """
    id: int
    name: str
    direction: str  # "input" or "output"
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def is_input(self) -> bool:
        return self.direction == "input"

    def is_output(self) -> bool:
        return self.direction == "output"

    def __str__(self):
        return f"{self.direction}:{self.id} {self.name}"


# -------------------------------------------------
# Device discovery
# -------------------------------------------------

def list_devices():
    """
    Return a list of all MIDI devices (inputs + outputs).
    """
    devices = []

    for i, name in enumerate(list_inputs()):
        devices.append(
            MidiDevice(
                id=i,
                name=name,
                direction="input",
            )
        )

    for i, name in enumerate(list_outputs()):
        devices.append(
            MidiDevice(
                id=i,
                name=name,
                direction="output",
            )
        )

    return devices


def list_input_devices():
    """
    Return MIDI input devices as MidiDevice objects.
    """
    return [
        MidiDevice(id=i, name=name, direction="input")
        for i, name in enumerate(list_inputs())
    ]


def list_output_devices():
    """
    Return MIDI output devices as MidiDevice objects.
    """
    return [
        MidiDevice(id=i, name=name, direction="output")
        for i, name in enumerate(list_outputs())
    ]


# -------------------------------------------------
# Device lookup
# -------------------------------------------------

def find_device(name: str, direction: str):
    """
    Find a device by name and direction.
    """
    if direction == "input":
        devices = list_input_devices()
    elif direction == "output":
        devices = list_output_devices()
    else:
        raise ValueError("direction must be 'input' or 'output'")

    for dev in devices:
        if dev.name == name:
            return dev

    return None