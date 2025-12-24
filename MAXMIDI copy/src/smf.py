# ---------------------------------------------------------------------------
#  MaxMidiSMF Struct (Python)
#
#  Converted from CMaxMidiSMF class
#  Binary-struct oriented design using struct module
#
#  Original work:
#  (C) Copyright, Paul A. Messick, 1996
# ---------------------------------------------------------------------------

import ctypes

READ = b'r'
WRITE = b'w'

# ---------------------------------------------------------------------------
# MaxMidiSMF struct using ctypes
# Mirrors C layout:
# HMIN    hSMF;               -> void* / handle (uint64)
# BOOL    fIsOpen;            -> int
# char    Mode;               -> char
# int     Format;             -> int
# int     nTracksInSMF;       -> int
# int     nTracksAttached;    -> int
# CMaxMidiTrack** pTrackList; -> void* (uint64)
# ---------------------------------------------------------------------------

class MaxMidiSMF(ctypes.Structure):
    _fields_ = [
        ("hSMF", ctypes.c_uint64),
        ("is_open", ctypes.c_int),
        ("mode", ctypes.c_char),
        ("format", ctypes.c_int),
        ("tracks_in_smf", ctypes.c_int),
        ("tracks_attached", ctypes.c_int),
        ("track_list_ptr", ctypes.c_uint64),  # pointer to array of track pointers
    ]

    def __init__(self):
        self.hSMF = 0
        self.is_open = 0
        self.mode = READ
        self.format = 0
        self.tracks_in_smf = 0
        self.tracks_attached = 0
        self.track_list_ptr = 0

    @property
    def is_open_bool(self) -> bool:
        return bool(self.is_open)

    @is_open_bool.setter
    def is_open_bool(self, value: bool):
        self.is_open = int(value)

    @property
    def mode_byte(self) -> bytes:
        return self.mode

    @mode_byte.setter
    def mode_byte(self, value: bytes):
        if value not in (READ, WRITE):
            raise ValueError("Mode must be READ or WRITE")
        self.mode = value

    # Binary serialization
    def to_bytes(self) -> bytes:
        return bytes(ctypes.string_at(ctypes.byref(self), ctypes.sizeof(self)))

    @classmethod
    def from_bytes(cls, data: bytes):
        if len(data) != ctypes.sizeof(cls):
            raise ValueError("Invalid struct size")
        obj = cls()
        ctypes.memmove(ctypes.byref(obj), data, len(data))
        return obj