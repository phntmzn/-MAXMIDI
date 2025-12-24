# ---------------------------------------------------------------------------
#  MaxMidiIn Struct (Python)
#
#  Converted from CMaxMidiIn class
#  Struct-backed, C-style design using Python's struct module
#
#  Original work:
#  (C) Copyright, Paul A. Messick, 1996
# ---------------------------------------------------------------------------

import ctypes

MAXPNAMELEN = 32        # typical Windows MIDI device name length
MIDIIN_DEFAULT = 0

class MaxMidiIn(ctypes.Structure):
    _fields_ = [
        ("hDevice", ctypes.c_uint64),                          # HMIN
        ("dwFlags", ctypes.c_uint32),                          # DWORD
        ("wDeviceID", ctypes.c_uint16),                        # WORD
        ("is_open", ctypes.c_int32),                           # BOOL
        ("description", ctypes.c_char * MAXPNAMELEN),          # char[MAXPNAMELEN]
        ("hParentWnd", ctypes.c_uint64),                       # HWND
        ("pSync", ctypes.c_uint64),                             # void*
        ("pTrack", ctypes.c_uint64),                            # void*
        ("is_started", ctypes.c_int32),                        # BOOL
    ]

    def __init__(self):
        super().__init__()
        self.hDevice = 0
        self.dwFlags = MIDIIN_DEFAULT
        self.wDeviceID = 0
        self.is_open = 0
        self.description = b""
        self.hParentWnd = 0
        self.pSync = 0
        self.pTrack = 0
        self.is_started = 0

    @property
    def description_str(self) -> str:
        return self.description.rstrip(b"\x00").decode("ascii")

    @description_str.setter
    def description_str(self, text: str):
        text_bytes = text.encode("ascii")[:MAXPNAMELEN]
        self.description[:len(text_bytes)] = text_bytes
        if len(text_bytes) < MAXPNAMELEN:
            self.description[len(text_bytes):] = b"\x00" * (MAXPNAMELEN - len(text_bytes))

    def to_bytes(self) -> bytes:
        """Serialize the structure to bytes."""
        return bytes(ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self)))

    @classmethod
    def from_bytes(cls, data: bytes):
        """Deserialize bytes into a MaxMidiIn instance."""
        if len(data) != ctypes.sizeof(cls):
            raise ValueError("Invalid struct size")
        obj = cls()
        ctypes.memmove(ctypes.addressof(obj), data, len(data))
        return obj

class MidiOut:
    def get_port_count(self) -> int:
        def get_port_name(self, index: int) -> str:
            def open(self, index: int):
                def close(self):
                    def send(self, status, data1, data2):
        
        